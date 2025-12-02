from django.shortcuts import get_object_or_404, render,redirect
from django.http import Http404, HttpResponse
from django.contrib import messages
from pygments.lexer import default

from session_client.utils import csv_room_report_response
from .models import RoomCalendarModel, TenantModel, BlocksModel
from .forms import RoomCalendarForm, TenantForm, LinkTenantForm, WeekCalendarForm, RoomReportForm, TenantReportForm, \
    RoomSwitchForm, BlockForm
from django.contrib.auth.decorators import login_required
from django_htmx.http import retarget, HttpResponseClientRefresh,trigger_client_event
from .calendar_utils import CalendarRender, CalendarClientsRender, CalendarBlocksRender
import pendulum as p
from session_client.models import SessionModel,ClientModel
from django.db.models import (Q, F, Case, When, FloatField, Count,
                              Sum, CharField,
                              Value, ExpressionWrapper,
                              Func,DateTimeField)
from django.db.models.functions import Concat,Cast

from .querysets import tenant_annotated_qs, get_tenant_qs_totals
import logging

logger = logging.getLogger(__name__)

@login_required
def week_view(request):
    """ Displays a calendar table with occurrences
        You can change the week to display or select a specific room calendar
       """
    sessions = (SessionModel.objects
                .filter(client__user=request.user)
                .select_related('client__user')
                .annotate(
                out_display=Concat(
                    F("client__tenant__display_name"),
                    Value("-"),
                    Cast("start_time",output_field=CharField(max_length=5)),
                    Value("-"),
                    Cast("end_time",output_field=CharField(max_length=5)),
                         output_field=CharField()),
                in_display=Concat(
                    F("client__code"),
                    Value("-"),
                    Cast("start_time",output_field=CharField(max_length=5)),
                    Value("-"),
                    Cast("end_time",output_field=CharField(max_length=5)),
                         output_field=CharField()),
                display=Case(When(client__user=request.user,then=F("in_display")),default=F("out_display")),
                start_datetime=ExpressionWrapper(
                    F("date")+F("start_time"),
                    output_field=DateTimeField()),
                end_datetime_adjusted=ExpressionWrapper(
                    F("date")+ F("end_time") - p.duration(minutes=30),
                    output_field=DateTimeField()),
            )

                )
    template = "room_calendar_app/dynamic/week_view.html"
    calendar_user = RoomCalendarModel.objects.filter(tenantmodel__user=request.user) #filter room_calendars options
    assert calendar_user is not None, "no room_calendars found"
    if request.POST:
        form_partial = WeekCalendarForm(data=request.POST)
        if form_partial.is_valid():
            """ main functionality changing content by date or calendar, 
            if calendar is empty all occurrences of user """
            date = form_partial.cleaned_data['date_reference']
            assert date is not None, "date should be something"
            ref_date_partial = p.datetime(date.year,date.month,date.day)
            room_calendar = None # To pass as info into the calendar object
            sessions = sessions.filter(date__week=ref_date_partial.week_of_year).select_related('client','client__user')
            if form_partial.cleaned_data['calendar']:
                room_calendar = form_partial.cleaned_data['calendar']
                sessions = sessions.filter(calendar=room_calendar)

            calendar_partial = CalendarRender(sessions=sessions,
                                              date_ref=ref_date_partial,
                                              room_cal=room_calendar
                                              )
            template_calendar = template + "#calendar-view-partial"
            context = {'calendar':calendar_partial}
            return render(request,template_calendar,context)
        # There should not be errors here but just in case
        form_partial_template = template + "#form-partial"
        form_partial.fields['calendar'].queryset = calendar_user
        context = {'form':form_partial}
        #response for form error
        response = render(request,form_partial_template,context)
        return retarget(response,"#calendar-form-tr") # retarget if not valid, switch week table (edge cases)
    #default GET response
    sessions = sessions.filter(date__week=p.now().week_of_year)
    form = WeekCalendarForm()
    form.fields['calendar'].queryset = calendar_user
    assert sessions is not None, "no sessions found"
    calendar = CalendarRender(sessions=sessions) # today by default
    context = {'calendar':calendar,'form':form}
    return render(request,template,context)

@login_required()
def week_view_auxiliary(request):
    clients = ClientModel.objects.filter(user=request.user)
    template = "room_calendar_app/auxiliary/client_list_li.html"
    context = {"clients":clients}
    return render(request,template,context)


@login_required
def room_calendar_listing_view(request):
    room_calendar_tenant = RoomCalendarModel.objects.filter(Q(tenantmodel__user=request.user)|Q(user=request.user)).prefetch_related("tenantmodel_set").distinct()
    context = {"calendar_tenant": room_calendar_tenant}
    return render(request,"room_calendar_app/display/room_calendar_list.html",context)

@login_required
def room_calendar_manage_view(request):
    ref_date = p.now()
    my_rooms = RoomCalendarModel.objects.filter(user=request.user)
    form = LinkTenantForm()
    form_tenant = TenantReportForm(initial={"month":ref_date.month})
    context = {"rooms": my_rooms, "form": form,"form_tenant":form_tenant}
    return render(request,"room_calendar_app/display/room_calendar_manage.html",context)

@login_required()
def room_manage_refresh_view(request,cal_pk):
    if request.method == "POST":
        form_tenant = TenantReportForm(initial={"month": p.now().month},
                                       data=request.POST)
        if form_tenant.is_valid():
            year = form_tenant.cleaned_data['year']
            month = form_tenant.cleaned_data['month']
            tenants_qs = tenant_annotated_qs(year,month,cal=cal_pk)
            totals = get_tenant_qs_totals(tenants_qs)
            template = "room_calendar_app/display/room_calendar_manage.html"+"#table-body-partial"
            context = {"tenants":tenants_qs,"totals":totals}
            return render(request,template,context)

        return Http404("Ups")
    return Http404("Ups")


@login_required
def room_calendar_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    template = "room_calendar_app/input/edit_calendar_modal.html"
    if request.method !='POST':
        #no data submitted; create a blank form
        form = RoomCalendarForm()
    else:
        #POST data submitted; process data
        form = RoomCalendarForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('room_calendar_app:room_calendar_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,template,context)

@login_required
def room_calendar_edit_view(request,room_calendar_pk):
    """edit the occurrence repetition erasing future events"""
    room_calendar = get_object_or_404(RoomCalendarModel,pk=room_calendar_pk,user=request.user)
    template = "room_calendar_app/input/edit_calendar_modal.html"
    if request.method !='POST':
        action = "Edit"
        #no data submitted; create a blank form
        form = RoomCalendarForm(instance=room_calendar)
    else:
        #POST data submitted; process data
        form = RoomCalendarForm(instance=room_calendar,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
    #display a blank or invalid form
    context = {'form':form,"room":room_calendar}
    return render(request,template,context)

@login_required
def tenant_view(request,tenant_pk):
    tenant = get_object_or_404(TenantModel, pk=tenant_pk)
    context = {"tenant": tenant}
    return render(request, "room_calendar_app/display/tenant_modal.html", context)

@login_required
def tenant_listing_view(request):
    """View a list of user's events """
    tenant_list = TenantModel.objects.filter(user=request.user)  #? I already changed this one
    context = {"tenant_list":tenant_list}
    return render(request, "room_calendar_app/dynamic/tenant_list.html", context)

@login_required
def tenant_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    if request.method !='POST':
        #no data submitted; create a blank form
        form = TenantForm()
        action = "Add"
    else:
        #POST data submitted; process data
        form = TenantForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            if request.htmx:
                return HttpResponseClientRefresh()
            return redirect('room_calendar_app:tenant_list')
    #display a blank or invalid form
    context = {'form':form,"action":action}
    return render(request,'room_calendar_app/input/add_tenant.html',context)



@login_required
def tenant_edit_view(request,tenant_pk):
    """edit the occurrence repetition erasing future events"""
    tenant = get_object_or_404(TenantModel,pk=tenant_pk,user=request.user)
    template = "room_calendar_app/input/add_tenant.html"
    form = TenantForm(instance=tenant)
    if request.method =='POST':
        #POST data submitted; process data
        form = TenantForm(instance=tenant,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
        form = TenantForm(instance=tenant)
        template = template + '#form-partial'
        context = {'form':form}
        return render(request,template,context)
    if request.htmx.target == 'modalBody':
        template = template + '#tenant-form-partial'
    context = {'tenant':tenant,'form':form}
    return render(request,template,context)

@login_required
def tenant_link_view(request,calendar_pk):
    """edit the occurrence repetition erasing future events"""
    calendar = get_object_or_404(RoomCalendarModel, pk=calendar_pk,user=request.user)
    template = "room_calendar_app/display/room_calendar_manage.html"
    if request.htmx:
        form = LinkTenantForm(data=request.POST)
        if form.is_valid():
            tenant_uuid = form.cleaned_data["tenant_id"]
            tenant = get_object_or_404(TenantModel,pk=tenant_uuid)
            tenant.calendar = calendar
            tenant.save()
            messages.info(request,"calendar linked to tenant")
            return HttpResponseClientRefresh()
        response =  render(request,template,{"form":form})
        return retarget(response,"tenant-link-form")
    else:
        return Http404

@login_required()
def tenant_unlink_view(request,tenant_pk):
    """edit the occurrence repetition erasing future events"""
    tenant = get_object_or_404(TenantModel,pk=tenant_pk,user=request.user)
    if request.htmx:
        #POST data submitted; process data
        """ render the list of tenants of a calendar back to htmx"""
        tenant.calendar = None
        tenant.save()
        messages.info(request,f"Tenant {tenant.display_name} unlinked")
        return HttpResponse()
    messages.warning(request,"Error when updating tenant")
    response = render(request,'_toasts.html')
    return retarget(response,"#modal-wrapper")


@login_required()
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
                                                   calendar=room,
                                                   ).exclude(attendance__exact="Cancel")
            template_partial = template + '#session-list-partial'
            if room.user != request.user:
                sessions.filter(client__user=request.user)
            sessions = sessions.annotate(
                pay=Case(
                    When(client__type="RoomP",
                         then=F("amount_paid") * room.percentage / 100),
                    default=room.cost,
                    output_field=FloatField()
                                )
                        )
            if request.htmx:
                totals = sessions.aggregate(session_count=Count("created_at"),
                                            session_pay=Sum("pay"))
                return render(request,template_partial,{'sessions':sessions,"totals":totals})
            return csv_room_report_response(sessions,room,month,year)
        template_form = template + '#form-partial'
        response = render(request,template_form,{'form':form})
        return retarget(response,'form-table-wrapper')
    form = RoomReportForm(initial={"month":p.now().month})
    sessions = SessionModel.objects.none()
    form.fields['room'].queryset = RoomCalendarModel.objects.filter(Q(user=request.user)|Q(tenantmodel__user=request.user))
    context = {'form':form,'sessions':sessions}
    return render(request,template,context)

@login_required()
def tenant_duplicate_hx(request,tenant_pk):
    if request.method == 'POST':
        tenant = TenantModel.objects.get(pk=tenant_pk)
        tenant_2 = TenantModel(name=tenant.name,
                               display_name=tenant.display_name,
                               description=tenant.description,
                               calendar=None,
                               user=request.user)
        tenant_2.save()
        tenant_2.refresh_from_db()
        template = 'room_calendar_app/dynamic/tenant_list.html'+'#tenant_item_partial'
        return render(request,template,{'tenant':tenant_2})
    return Http404("ups, page not wat you thought")

@login_required()
def tenant_delete_hx(request,tenant_pk):
    tenant = TenantModel.objects.get(pk=tenant_pk)
    tenant.delete()
    return HttpResponseClientRefresh()

@login_required()
def week_blocks_view(request):
    template = "room_calendar_app/dynamic/week_view_blocks.html"
    if request.method =='POST':
        form = RoomSwitchForm(data=request.POST)
        if form.is_valid():
            room = form.cleaned_data['room']
            blocks = BlocksModel.objects.filter(tenant__calendar=room)
            calendar = CalendarBlocksRender(blocks,calendar=room)
            template_partial = template + "#calendar-table-partial"
            return render(request,template_partial,{"calendar":calendar})
    blocks = BlocksModel.objects.none()
    room_qs = RoomCalendarModel.objects.filter(Q(tenantmodel__user=request.user)|Q(user=request.user))
    calendar = CalendarBlocksRender(blocks)
    form = RoomSwitchForm(initial={"room":room_qs[0]})
    form.fields["room"].queryset = room_qs
    context = {"calendar": calendar, "form": form}
    return render(request, template, context)

@login_required()
def week_schedule_view(request):
    template = "room_calendar_app/dynamic/week_view_clients.html"
    if request.method =='POST':
        form = RoomSwitchForm(data=request.POST)
        if form.is_valid():
            room = form.cleaned_data['room']
            clients = ClientModel.objects.filter(tenant__calendar=room) or None
            calendar = CalendarClientsRender(clients,calendar=room)
            template_partial = template + "#calendar-table-partial"
            return render(request,template_partial,{"calendar":calendar})
    clients = ClientModel.objects.filter(user=request.user) or None
    calendar = CalendarClientsRender(clients)
    form = RoomSwitchForm()
    form.fields["room"].queryset = RoomCalendarModel.objects.filter(Q(tenantmodel__user=request.user)|Q(user=request.user))
    context = {"calendar":calendar,"form":form}
    return render(request,template,context)

@login_required()
def block_add_view(request,day=None,time=None,room=None):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    template = 'room_calendar_app/input/add_block.html'
    if request.method =='POST':
        #POST data submitted; process data
        form = BlockForm(data=request.POST)
        logger.debug("method post received")
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            logger.debug("form saved")
            response = HttpResponse(request)
            response = trigger_client_event(response,"RefreshTable",{"target":"#room-switch-form"})
            return trigger_client_event(response,"CloseModal",{"target":"#modal"})
        logger.debug("form errors")
        template_partial = template + '#block-form-partial'
        return render(request,template_partial,{"form":form})
    start_time = p.parse(time).time()
    initial = {"day":day,"start_time":start_time,"end_time":start_time.add(hours=1)}
    tenant_filter = Q(user=request.user)
    if room:
        initial['room'] = room
        tenant_filter &= Q(calendar__pk=room)
    form = BlockForm(data=initial)
    form.fields["tenant"].queryset = TenantModel.objects.filter(tenant_filter)
    logger.debug("form with initials")
    context = {'form':form}
    #display a blank or invalid form
    return render(request,template,context)

@login_required()
def block_edit_view(request,block_pk=None):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    template = 'room_calendar_app/input/add_block.html'
    block = get_object_or_404(BlocksModel,pk=block_pk)
    assert isinstance(block,BlocksModel)
    form = BlockForm(instance=block)
    if request.method =='POST':
        #POST data submitted; process data
        form = BlockForm(data=request.POST,instance=block)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
        template_partial = template + '#block-form-partial'
        return render(request,template_partial,{"form":form})
    context = {'form':form,"block_item":block}
    return render(request,template,context)

@login_required()
def block_delete_view(request,block_pk):
    block = get_object_or_404(BlocksModel,pk=block_pk)
    block.delete()
    logger.debug("block deleted")
    return HttpResponseClientRefresh()