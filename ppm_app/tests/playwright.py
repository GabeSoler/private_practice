import os
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


class LiveTest(StaticLiveServerTestCase):
    @classmethod
    def setUp(cls):
        cls.user = get_user_model().objects.create(username="Gabriel", email="test@gabriel.cl")
        cls.user.set_password("password")
        cls.user.save()

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
