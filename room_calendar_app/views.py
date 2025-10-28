from pyexpat.errors import messages

from django.shortcuts import get_object_or_404, render,redirect
from django.http import Http404

from session_client.utils import date_plus_time, time_plus_duration
from .models import RoomCalendarModel,TenantModel
from .forms import RoomCalendarForm,TenantForm,LinkTenantForm,WeekCalendarForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django_htmx.http import retarget, HttpResponseClientRefresh
from .calendar_utils import CalendarRender
import pendulum as p
from session_client.models import SessionModel,ClientModel

def check_owner(topic_owner,request_user):
    if topic_owner != request_user:
        raise Http404
    

@login_required
@cache_control(private=True)
def week_view(request):
    """ Displays a calendar table with occurrences
        You can change the week to display or select a specific room calendar
       """
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
            sessions = (SessionModel.objects
                        .filter(client__user=request.user,
                                             date__week=ref_date_partial.week_of_year)
                        .select_related('client','client__user'))
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
    form = WeekCalendarForm()
    form.fields['calendar'].queryset = calendar_user
    sessions = (SessionModel.objects
                .filter(client__user=request.user,
                                           date__week=p.now().week_of_year)
                .select_related('client','client__user'))
    assert sessions is not None, "no sessions found"
    calendar = CalendarRender(sessions=sessions) # today by default
    context = {'calendar':calendar,'form':form}
    return render(request,template,context)

def week_view_auxiliary(request):
    clients = ClientModel.objects.filter(user=request.user)
    template = "room_calendar_app/auxiliary/client_list_li.html"
    context = {"clients":clients}
    return render(request,template,context)


@login_required
def room_calendar_listing_view(request):
    room_calendar_tenant = RoomCalendarModel.objects.filter(tenantmodel__user=request.user).prefetch_related("tenantmodel_set").distinct()
    context = {"calendar_tenant": room_calendar_tenant}
    return render(request,"room_calendar_app/display/room_calendar_list.html",context)

@login_required
def room_calendar_manage_view(request):
    my_rooms = RoomCalendarModel.objects.filter(user=request.user).prefetch_related("tenantmodel_set")
    form = LinkTenantForm()
    context = {"rooms": my_rooms, "form": form}
    return render(request,"room_calendar_app/display/room_calendar_manage.html",context)

@login_required
def room_calendar_view(request,calendar_pk):
    calendar = get_object_or_404(RoomCalendarModel, pk=calendar_pk,user=request.user)
    tenants = calendar.tenantmodel_set.all()
    form = LinkTenantForm()
    template = "room_calendar_app/dynamic/room_calendar.html"
    if request.htmx:
        form = LinkTenantForm(data=request.POST)
        form_template = template + '#form-partial'
        if form.is_valid():
            tenant_list_template = template + '#tenant-list'
            tenant_uuid = form.cleaned_data["tenant_id"]
            tenant = get_object_or_404(TenantModel,pk=tenant_uuid)
            calendar.tenants.add(tenant)
            tenants = calendar.tenants.all()
            context = {"tenants":tenants}
            response = render(request,tenant_list_template,context)
            return retarget(response,'#tenant-list-wrapper')
        context = {'form':form}
        return render(request,form_template,context)
    context = {"calendar": calendar,"tenants":tenants,'form':form}
    return render(request,template,context)


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
            return redirect('room_calendar_app:tenant_list')
    #display a blank or invalid form
    context = {'form':form,"action":action}
    return render(request,'room_calendar_app/input/add_tenant.html',context)



@login_required
def tenant_edit_view(request,tenant_pk):
    """edit the occurrence repetition erasing future events"""
    tenant = TenantModel.objects.get(pk=tenant_pk)
    template = "room_calendar_app/input/add_tenant.html"
    form = TenantForm(instance=tenant)
    if request.method =='POST':
        #POST data submitted; process data
        check_owner(tenant.user,request.user)
        form = TenantForm(instance=tenant,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
        form = TenantForm(instance=tenant)
        template = template + '#form-partial'
        context = {'form':form}
        return render(request,template,context)
    if request.htmx:
        template = template + '#tenant-form-partial'
    context = {'tenant':tenant,'form':form}
    return render(request,template,context)

@login_required
def tenant_link_view(request,calendar_pk):
    """edit the occurrence repetition erasing future events"""
    calendar = get_object_or_404(RoomCalendarModel,pk=calendar_pk,user=request.user)
    template = "room_calendar_app/display/room_calendar_manage.html"
    if request.method == "POST":
        #POST data submitted; process data
        form = LinkTenantForm(data=request.POST)
        if form.is_valid():
            """ render the list of tenants of a calendar back to htmx"""
            tenant_uuid = form.cleaned_data["tenant_id"]
            calendar.tenants.add(tenant_uuid)
            template = template + "#table-body-partial"
            return render(request,template,{"calendar":calendar})
        response =  render(request,template,{"form":form})
        return retarget(response,"tenant-link-form")
    else:
        return Http404


def tenant_unlink_view(request,tenant_pk):
    """edit the occurrence repetition erasing future events"""
    calendar = get_object_or_404(RoomCalendarModel,tenants__pk=tenant_pk,user=request.user)
    template = "room_calendar_app/display/room_calendar_manage.html"
    if request.method == "PATCH":
        #POST data submitted; process data
        """ render the list of tenants of a calendar back to htmx"""
        calendar.tenants.remove(tenant_pk)
        template = template + "#table-body-partial"
        return render(request,template,{"calendar":calendar})
    messages.warning(request,"Error when updating tenant")
    response = render(request)
    return retarget(response,"modal-wrapper")




