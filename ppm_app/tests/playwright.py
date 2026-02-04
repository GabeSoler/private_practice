import os
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright, expect

from django.conf import settings


class LiveTest(StaticLiveServerTestCase):
    @classmethod
    def setUp(cls):
        cls.user = get_user_model().objects.create(username="Gabriel", email="test@gabriel.cl")
        cls.user.set_password("password")
        cls.user.save()

    def force_login(self, page):
        self.client.force_login(self.user)
        session_cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]

        context = page.context
        context.add_cookies([{
            'name': settings.SESSION_COOKIE_NAME,
            'value': session_cookie.value,
            'domain': self.live_server_url.split('://')[-1].split(':')[0],
            'path': '/',
        }])

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def test_index(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url + reverse('base:index'))
        page.wait_for_selector('text=Dreamy')
        page.get_by_role("link", name="Dreamy").click()
        expect(page.get_by_role("heading", name="Calendar View")).to_be_visible()
        expect(page.get_by_role("heading", name="Rooms management")).to_be_visible()
        page.locator("i").nth(5).click()
        page.locator("i").nth(5).click()
        page.locator("i").nth(5).click()
        expect(page.get_by_role("main")).to_contain_text("Sessions that are currently open past current date")
        # Check for the Features section
        self.assertTrue(page.is_visible('text=Features'))
        page.close()

    def test_login(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url + reverse('accounts:login'))
        page.wait_for_selector('text=Password')
        page.fill('[name=username]', self.user.username)
        page.fill('[name=password]', 'password')
        page.click('button:has-text("Log in")')
        # After login, we should see the Logout button
        page.wait_for_selector('text=Logout')
        self.assertTrue(page.is_visible('text=Logout'))
        # And the welcome message
        self.assertTrue(page.is_visible(f'text=Hello, {self.user.username}!'))
        page.close()

    def test_create_client(self):
        page = self.browser.new_page()
        self.force_login(page)
        page.goto(self.live_server_url + reverse('base:index'))
        # No need to click Login or fill the form any more
        page.locator("#clients-link-top-nav").click()
        page.locator("#add-client-link").click()
        page.get_by_role("textbox", name="Code").click()
        page.get_by_role("textbox", name="Code").fill("TEST123")
        page.locator("#id_tenant").select_option("1")
        page.locator("#id_time").select_option("10:30:00")
        page.get_by_role("button", name="Save").click()
        page.close()
