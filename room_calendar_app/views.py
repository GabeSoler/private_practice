from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse
from django.contrib import messages

from ppm_app.responses.hx_responses import ok_response_modal
from session_client.utils import csv_room_report_response
from .models import RoomCalendarModel, TenantModel, BlocksModel
from .forms import RoomCalendarForm, TenantForm, LinkTenantForm, WeekCalendarForm, RoomReportForm, TenantReportForm, \
    RoomSwitchForm, BlockForm
from django_htmx.http import retarget, HttpResponseClientRefresh, trigger_client_event, reswap
from .calendar_utils import CalendarRender, CalendarTimesRender, CalendarBlocksRender, MonthNextUtil
import pendulum as p
from session_client.models import SessionModel, ClientModel, ClientTimes
from django.db.models import (Q, F, Case, When, FloatField, Count,
                              Sum)
from .querysets import tenant_annotated_qs, get_tenant_qs_totals, week_view_session_qs
import logging

logger = logging.getLogger(__name__)


def week_view(request):
    """ Displays a calendar table with occurrences
        You can change the week to display or select a specific room calendar
       """
    sessions = week_view_session_qs(request.user)
    template = "room_calendar_app/dynamic/week_view.html"
    calendar_user = RoomCalendarModel.objects.filter(
        Q(tenantmodel__user=request.user) | Q(user=request.user)).distinct()  # filter room_calendars options
    assert calendar_user is not None, "no room_calendars found"
    if request.POST:
        form_partial = WeekCalendarForm(data=request.POST)
        if form_partial.is_valid():
            """ main functionality changing content by date or calendar, 
            if calendar is empty all occurrences of user """
            logger.debug("form valid")
            date = form_partial.cleaned_data['date_reference']
            assert date is not None, "date should be something"
            ref_date_partial = p.datetime(date.year, date.month, date.day)
            room_calendar = None  # To pass as info into the calendar object
            sessions = sessions.filter(date__week=ref_date_partial.week_of_year).select_related('client',
                                                                                                'client__user')
            if form_partial.cleaned_data['calendar']:
                room_calendar = form_partial.cleaned_data['calendar']
                sessions = sessions.filter(tenant__calendar=room_calendar)

            calendar_partial = CalendarRender(sessions=sessions,
                                              date_ref=ref_date_partial,
                                              room_cal=room_calendar
                                              )
            template_calendar = template + "#calendar-view-partial"
            form_partial.fields['calendar'].queryset = calendar_user
            context = {'calendar': calendar_partial, 'form': form_partial}
            return render(request, template_calendar, context)
        # There should not be errors here but just in case
        logger.debug(form_partial.errors)
        messages.error(request, "error on request")
        response = render(request, "_toasts.html")
        return retarget(response, "#modal-wrapper")  # retarget if not valid, switch week table (edge cases)
    # default GET response
    logger.debug("rendering week view")
    sessions = sessions.filter(date__week=p.now().week_of_year)
    form = WeekCalendarForm()
    form.fields['calendar'].queryset = calendar_user
    assert sessions is not None, "no sessions found"
    calendar = CalendarRender(sessions=sessions, date_ref=p.now())  # today by default
    context = {'calendar': calendar, 'form': form}
    return render(request, template, context)


def week_blocks_view(request):
    template = "room_calendar_app/dynamic/week_view_blocks.html"
    room_qs = RoomCalendarModel.objects.filter(Q(tenantmodel__user=request.user) | Q(user=request.user)).distinct()
    if request.method == 'POST':
        form = RoomSwitchForm(data=request.POST)
        if form.is_valid():
            room_cal = None
            if form.cleaned_data['calendar']:
                room_cal = form.cleaned_data['calendar']
                blocks = BlocksModel.objects.filter(tenant__calendar=room_cal)
            else:
                blocks = BlocksModel.objects.filter(tenant__user=request.user)
            calendar = CalendarBlocksRender(blocks, room_cal=room_cal)
            template_partial = template + "#calendar-table-partial"
            form.fields["calendar"].queryset = room_qs
            context = {"calendar": calendar, "form": form}
            return render(request, template_partial, context)
        messages.error(request, "error on request")
        logger.warning(form.errors)
        response = render(request, "_toasts.html")
        return retarget(response, "#modal-wrapper")
    blocks = BlocksModel.objects.filter(tenant__user=request.user)
    calendar = CalendarBlocksRender(blocks)
    form = RoomSwitchForm(initial={"room": room_qs[0]})
    form.fields["calendar"].queryset = room_qs
    context = {"calendar": calendar, "form": form}
    return render(request, template, context)


def week_client_defaults_view(request):
    template = "room_calendar_app/dynamic/week_view_clients.html"
    room_qs = (RoomCalendarModel.objects.
               filter(Q(tenantmodel__user=request.user) | Q(user=request.user))).distinct()
    times = ClientTimes.objects.filter(client__user=request.user).annotate(
        end_time=F("time") + F("client__duration"),
        client_code=F("client__code"),
        duration=F("client__duration"))
    if request.method == 'POST':
        form = RoomSwitchForm(data=request.POST)
        if form.is_valid():
            room_cal = None
            if form.cleaned_data['calendar']:
                room_cal = form.cleaned_data['calendar']
                times = times.filter(tenant__calendar=room_cal)
            calendar = CalendarTimesRender(times, room_cal=room_cal)
            template_partial = template + "#calendar-table-partial"
            form.fields["calendar"].queryset = room_qs
            context = {"calendar": calendar, "form": form}
            return render(request, template_partial, context)
        messages.error(request, "error on request")
        logger.warning(form.errors)
        response = render(request, "_toasts.html")
        return retarget(response, "#modal-wrapper")
    calendar = CalendarTimesRender(times)
    form = RoomSwitchForm()
    form.fields["calendar"].queryset = room_qs
    context = {"calendar": calendar, "form": form}
    return render(request, template, context)


def room_calendar_listing_view(request):
    my_rooms = RoomCalendarModel.objects.filter(tenantmodel__user=request.user).distinct()
    date_initial = p.now()
    context = {"my_rooms": my_rooms, "date_initial": date_initial}
    return render(request, "room_calendar_app/display/room_calendar_list.html", context)


def room_calendar_manage_view(request):
    ref_date = p.now()
    my_rooms = RoomCalendarModel.objects.filter(user=request.user)
    form_tenant = TenantReportForm(initial={"month": ref_date.month})
    context = {"rooms": my_rooms, "form_tenant": form_tenant}
    return render(request, "room_calendar_app/display/room_calendar_manage.html", context)


def room_manage_refresh_view(request, cal_uuid):
    if request.method == "POST":
        form_tenant = TenantReportForm(initial={"month": p.now().month},
                                       data=request.POST)
        if form_tenant.is_valid():
            year = form_tenant.cleaned_data['year']
            month = form_tenant.cleaned_data['month']
            tenants_qs = tenant_annotated_qs(year, month, cal_uuid=cal_uuid)
            totals = get_tenant_qs_totals(tenants_qs)
            template = "room_calendar_app/auxiliary/tenant_list_info.html" + "#table-body-partial"
            context = {"tenants": tenants_qs, "totals": totals}
            return render(request, template, context)
        return Http404("Ups")
    return Http404("Ups")


def room_list_refresh_view(request):
    if request.method == "POST":
        form = WeekCalendarForm(data=request.POST)
        logger.debug("form post received")
        if form.is_valid():
            logger.debug("form valid")
            room_cal = form.cleaned_data['calendar'] or None
            date_ref = p.instance(form.cleaned_data['date_reference'])
            month_util = MonthNextUtil(date_ref, room_cal)
            tenants_qs = tenant_annotated_qs(date_ref.year,
                                             date_ref.month,
                                             cal_id=room_cal.pk,
                                             user=request.user)  # to get right to pay numbers in totals
            totals = get_tenant_qs_totals(tenants_qs)
            template = "room_calendar_app/display/room_calendar_list.html" + "#calendar_info_partial"
            context = {"totals": totals, "month_util": month_util, "calendar": room_cal}
            return render(request, template, context)
        logger.debug(form.errors)
        messages.error(request, f"Error")
        response = render(request, "_toasts.html")
        return retarget(response, "#modal-wrapper")
    return Http404("Ups")


def room_calendar_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    template = "room_calendar_app/input/edit_calendar_modal.html"
    if request.method != 'POST':
        # no data submitted; create a blank form
        form = RoomCalendarForm()
    else:
        # POST data submitted; process data
        form = RoomCalendarForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return HttpResponseClientRefresh()
    # display a blank or invalid form
    context = {'form': form}
    return render(request, template, context)


def room_calendar_edit_view(request, room_calendar_uuid):
    """edit the occurrence repetition erasing future events"""
    room_calendar = get_object_or_404(RoomCalendarModel, uuid=room_calendar_uuid, user=request.user)
    template = "room_calendar_app/input/edit_calendar_modal.html"
    if request.method != 'POST':
        action = "Edit"
        # no data submitted; create a blank form
        form = RoomCalendarForm(instance=room_calendar)
    else:
        # POST data submitted; process data
        form = RoomCalendarForm(instance=room_calendar, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
    # display a blank or invalid form
    context = {'form': form, "room": room_calendar}
    return render(request, template, context)


def tenant_view(request, tenant_uuid):
    tenant = get_object_or_404(TenantModel, pk=tenant_uuid)
    context = {"tenant": tenant}
    return render(request, "room_calendar_app/display/tenant_modal.html", context)


def tenant_listing_view(request):
    """View a list of user's events """
    tenant_list = TenantModel.objects.filter(user=request.user)  # ? I already changed this one
    form = LinkTenantForm()
    context = {"tenant_list": tenant_list, "form": form}
    return render(request, "room_calendar_app/dynamic/tenant_list.html", context)


def tenant_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    if request.method != 'POST':
        # no data submitted; create a blank form
        form = TenantForm()
        action = "Add"
    else:
        # POST data submitted; process data
        form = TenantForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            if request.htmx:
                return HttpResponseClientRefresh()
            return redirect('room_calendar_app:tenant_list')
    # display a blank or invalid form
    context = {'form': form}
    return render(request, 'room_calendar_app/input/add_tenant.html', context)


def tenant_edit_view(request, tenant_uuid):
    """edit the occurrence repetition erasing future events"""
    tenant = get_object_or_404(TenantModel, uuid=tenant_uuid, user=request.user)
    template = "room_calendar_app/input/add_tenant.html"
    form = TenantForm(instance=tenant)
    if request.method == 'POST':
        # POST data submitted; process data
        form = TenantForm(instance=tenant, data=request.POST)
        if form.is_valid():
            form.save()
            logger.debug(f"{p.now()} - form tenant saved")
            return ok_response_modal(request,
                                     "Tenant Saved",
                                     event_and_target=("RefreshTable", "#hx-helper"))
        form = TenantForm(instance=tenant)
        template = template + '#tenant-form-partial'
        context = {'form': form}
        return render(request, template, context)
    if request.htmx.target == 'modalBody':
        template = template + '#tenant-form-partial'
    context = {'tenant': tenant, 'form': form}
    return render(request, template, context)


def tenant_link_view(request, tenant_uuid):
    """edit the occurrence repetition erasing future events"""
    tenant = get_object_or_404(TenantModel, uuid=tenant_uuid, user=request.user)
    if request.htmx:
        form = LinkTenantForm(data=request.POST)
        if form.is_valid():
            room_uuid = form.cleaned_data["room_id"]
            room = RoomCalendarModel.objects.filter(uuid=room_uuid).first()
            if not room:
                form.add_error('room_id', "Room not found")
                status = "warning"
            elif tenant.calendar is room:
                form.add_error('room_id', "Same room")
                status = "warning"
            else:
                form = LinkTenantForm()
                status = "success"
            tenant.calendar = room
            tenant.save()
            template_partial = "room_calendar_app/dynamic/tenant_list.html" + "#tenant_item_partial"
            context = {'tenant': tenant, "form": form, "status": status}
            return render(request, template_partial, context)
        template_form = "room_calendar_app/auxiliary/tenant-link-form.html" + "#form-partial"
        response = render(request, template_form, {"form": form, "tenant": tenant})
        response = retarget(response, f"#tenant-link-form-{tenant_uuid}")
        return reswap(response, "innerHTML")
    else:
        return Http404


def tenant_unlink_view(request, tenant_uuid):
    """edit the occurrence repetition erasing future events"""
    tenant = get_object_or_404(TenantModel, uuid=tenant_uuid, user=request.user)
    if request.htmx:
        # POST data submitted; process data
        """ render the list of tenants of a calendar back to htmx"""
        tenant.calendar = None
        tenant.save()
        messages.info(request, f"Tenant {tenant.display_name} unlinked")
        return HttpResponse()
    messages.warning(request, "Error when updating tenant")
    response = render(request, '_toasts.html')
    return retarget(response, "#modal-wrapper")


def room_report_view(request):
    template = 'room_calendar_app/display/room_report.html'
    if request.method == 'POST':
        form = RoomReportForm(data=request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            room = form.cleaned_data['room']
            sessions = SessionModel.objects.filter(date__month=month,
                                                   date__year=year,
                                                   tenant__calendar=room,
                                                   ).exclude(attendance__exact="Cancel")
            template_partial = template + '#session-list-partial'
            if room.user != request.user:
                sessions.filter(client__user=request.user)
            sessions = sessions.annotate(
                pay=Case(
                    When(tenant__agreement="Percentage",
                         then=F("fee") * room.percentage / 100),
                    default=room.cost,
                    output_field=FloatField()
                )
            )
            if request.htmx:
                totals = sessions.aggregate(session_count=Count("created_at"),
                                            session_pay=Sum("pay"))
                return render(request, template_partial, {'sessions': sessions, "totals": totals})
            return csv_room_report_response(sessions, room, month, year)
        template_form = template + '#form-partial'
        response = render(request, template_form, {'form': form})
        return retarget(response, 'form-table-wrapper')
    form = RoomReportForm(initial={"month": p.now().month})
    sessions = SessionModel.objects.none()
    form.fields['room'].queryset = RoomCalendarModel.objects.filter(
        Q(user=request.user) | Q(tenantmodel__user=request.user)).distinct()
    context = {'form': form, 'sessions': sessions}
    return render(request, template, context)


def tenant_duplicate_hx(request, tenant_uuid):
    if request.method == 'POST':
        tenant = TenantModel.objects.get(uuid=tenant_uuid)
        tenant_2 = TenantModel(name=tenant.name,
                               display_name=tenant.display_name,
                               description=tenant.description,
                               calendar=None,
                               user=request.user)
        tenant_2.save()
        tenant_2.refresh_from_db()
        template = 'room_calendar_app/dynamic/tenant_list.html' + '#tenant_item_partial'
        form = LinkTenantForm()
        return render(request, template, {'tenant': tenant_2, 'form': form})
    return Http404("ups, page not wat you thought")


def tenant_delete_hx(request, tenant_uuid):
    tenant = TenantModel.objects.get(uuid=tenant_uuid)
    tenant.delete()
    return HttpResponseClientRefresh()


def block_add_view(request, day=None, time=None, room=None):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    template = 'room_calendar_app/input/add_block.html'
    if request.method == 'POST':
        # POST data submitted; process data
        form = BlockForm(data=request.POST)
        logger.debug("method post received")
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            saved, overlap = instance.save_with_checks()
            if saved:
                logger.debug(f"{p.now()} - form blocks saved")
                return ok_response_modal(request,
                                         "Block Added",
                                         event_and_target=("RefreshTable", "#caption-form"))
            logger.debug(f"{p.now()} - form blocks not saved")
            form.add_error("day", "❗Block Overlaps with another")
        logger.debug("form blocks errors")
        template_partial = template + '#block-form-partial'
        form.fields["tenant"].queryset = TenantModel.objects.filter(user=request.user, calendar=room)
        form.fields["tenant"].label_from_instance = lambda obj: obj.display_name
        return render(request, template_partial, {"form": form, "calendar_pk": room})
    initial = {}
    if day and time:
        start_time = p.parse(time).time()
        initial = {"day": day - 1, "start_time": start_time, "end_time": start_time.add(hours=1)}
    form = BlockForm(initial=initial)
    form.fields["tenant"].queryset = TenantModel.objects.filter(user=request.user, calendar=room)
    form.fields["tenant"].label_from_instance = lambda obj: obj.display_name
    logger.debug("form with initials")
    context = {'form': form, "calendar_pk": room}
    # display a blank or invalid form
    return render(request, template, context)


def block_edit_view(request, block_pk):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    template = 'room_calendar_app/input/add_block.html'
    block = get_object_or_404(BlocksModel, pk=block_pk)
    assert isinstance(block, BlocksModel)
    form = BlockForm(instance=block)
    if request.method == 'POST':
        # POST data submitted; process data
        form = BlockForm(data=request.POST, instance=block)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save_with_checks()
            logger.debug(f"{p.now()} - form blocks saved")
            return ok_response_modal(request,
                                     "Block Added",
                                     event_and_target=("RefreshTable", "#caption-form"))
        template_partial = template + '#block-form-partial'
        return render(request, template_partial, {"form": form})
    context = {'form': form, "block_item": block}
    return render(request, template, context)


def block_delete_view(request, block_uuid):
    block = get_object_or_404(BlocksModel, uuid=block_uuid)
    block.delete()
    logger.debug("block deleted")
    return HttpResponseClientRefresh()
