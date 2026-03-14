import pprint

from django.test import TestCase
from django.urls import reverse

from .forms import TenantForm, RoomReportForm, BlockForm
from .models import RoomCalendarModel, TenantModel, BlocksModel
from django.utils import translation
import pendulum as p
from .tests import MetaTestSetupMixin


class PostMethodTests(MetaTestSetupMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        user_language = "en"
        translation.activate(user_language)

    def test_week_view_post(self):
        url = reverse('room_calendar_app:week_view')
        data = {
            'date_reference': p.now().format('YYYY-MM-DD'),
            'calendar': self.room_1.pk
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "calendar")

    def test_room_manage_refresh_view_post(self):
        url = reverse('room_calendar_app:room_manage_refresh', args=[self.room_1.uuid])
        data = {
            'month': p.now().month,
            'year': p.now().year,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tenant.name)  # tenant display_name

    def test_room_list_refresh_view_post(self):
        url = reverse('room_calendar_app:room_list_refresh')
        ref_date = p.now().add(months=1)
        data = {
            'date_reference': ref_date.format('YYYY-MM-DD'),
            'calendar': self.room_1.pk
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ref_date.format("YY-MM"))  # tenant display_name

    def test_room_calendar_add_view_post(self):
        url = reverse('room_calendar_app:add_room_calendar')
        data = {
            'name': 'New Room',
            'description': 'Description',
            'percentage': 10,
            'cost': 20,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(RoomCalendarModel.objects.filter(name='New Room').exists())

    def test_room_calendar_edit_view_post(self):
        url = reverse('room_calendar_app:edit_room_calendar', args=[self.room_default.uuid])
        data = {
            'name': 'Updated Room',
            'description': 'Updated Description',
            'percentage': 15,
            'cost': 25,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.room_default.refresh_from_db()
        self.assertEqual(self.room_default.name, 'Updated Room')

    def test_tenant_add_view_post(self):
        url = reverse('room_calendar_app:add_tenant')
        data = {
            'display_name': 'New Tenant',
            'name': 'new_tenant',
            'description': 'Some description',
            'agreement': 'Percentage',
        }
        form = TenantForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'errorlist')
        self.assertTrue(TenantModel.objects.filter(display_name='New Tenant').exists())

    def test_tenant_edit_view_post(self):
        url = reverse('room_calendar_app:edit_tenant', args=[self.tenant.uuid])
        data = {
            'display_name': 'Updated Tenant',
            'name': 'updated_tenant',
            'description': 'Updated description',
            'agreement': 'Percentage',
        }
        form = TenantForm(data, instance=self.tenant)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.display_name, 'Updated Tenant')

    def test_tenant_link_view_post(self):
        url = reverse('room_calendar_app:link_tenant', args=[self.tenant.uuid])
        data = {'room_id': str(self.room_2.uuid)}
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.calendar, self.room_2)

    def test_tenant_unlink_view_post(self):
        # tenant_unlink_view doesn't explicitly check for POST, but handles HTMX request
        url = reverse('room_calendar_app:unlink_tenant', args=[self.tenant.uuid])
        response = self.client.post(url, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertIsNone(self.tenant.calendar)

    def test_room_report_view_post(self):
        url = reverse('room_calendar_app:room_report')
        data = {
            'room': self.room_1.pk,
            'month': p.now().month,
            'year': p.now().year,
        }
        form = RoomReportForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session_1.date.strftime('%B %d, %Y'))

    def test_tenant_duplicate_hx_post(self):
        url = reverse('room_calendar_app:duplicate_tenant', args=[self.tenant.uuid])
        response = self.client.post(url, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TenantModel.objects.filter(display_name=self.tenant.display_name).count() > 1)

    def test_week_blocks_view_post(self):
        """ testing the blocks view, so it shows tenants inside the room
        in this case, tenant has room_1 as a foreign key so it should belong there,
        Using a block with a tennat host with room 1, it tests name change

        """
        from .forms import RoomSwitchForm
        url = reverse('room_calendar_app:week_blocks_view')
        response = self.client.get(url, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tenant.name)
        data = {'calendar': self.room_1.pk}
        form = RoomSwitchForm(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "errorlist")
        self.assertContains(response, self.tenant.name)
        self.assertContains(response, self.tenant_host_room_1.display_name)
        self.assertNotContains(response, self.tenant_host_room_1.name)

    def test_week_schedule_view_post(self):
        url = reverse('room_calendar_app:week_client_defaults_view')
        data = {'room': self.room_1.pk}
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.client_instance.code)

    def test_block_add_view_post(self):
        url = reverse('room_calendar_app:block_add_view')
        data = {
            'tenant': self.tenant.pk,
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'day': 1,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "id_tenant_helptext")
        self.assertTrue(BlocksModel.objects.filter(tenant=self.tenant, start_time='10:00:00').exists())

    def test_block_edit_view_post(self):
        block = BlocksModel.objects.create(
            tenant=self.tenant,
            start_time='09:00:00',
            end_time='10:00:00',
            day=1,
        )
        url = reverse('room_calendar_app:block_edit', args=[block.pk])
        data = {
            'tenant': self.tenant.pk,
            'start_time': '11:00:00',
            'end_time': '12:00:00',
            'day': 2,
        }
        form = BlockForm(data, instance=block)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        block.refresh_from_db()
        self.assertNotContains(response, "id_tenant_helptext")
        self.assertTrue(BlocksModel.objects.filter(tenant=self.tenant, start_time='11:00:00').exists())

    def test_block_delete_view_post(self):
        block = BlocksModel.objects.create(
            tenant=self.tenant,
            start_time='09:00:00',
            end_time='10:00:00',
            day=1,
        )
        # block_delete_view doesn't explicitly check for POST, but we can call it with POST
        url = reverse('room_calendar_app:delete_block', args=[block.uuid])
        response = self.client.post(url, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BlocksModel.objects.filter(pk=block.pk).exists())
