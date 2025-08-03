from django.shortcuts import get_object_or_404, render,redirect
from django.http import Http404

from .models import RoomCalendarModel,TenantModel
from .forms import RoomCalendarForm,TenantForm,LinkTenantForm,WeekCalendarForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django_htmx.http import retarget
from .calendar_utils import CalendarRender
import pendulum as p
from session_client.models import SessionModel,ClientModel
from session_client.forms import ClientSessionForm,StartDateSessionForm
from django.contrib import messages

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
    room_calendar_user = RoomCalendarModel.objects.filter(tenants__user=request.user) #filter room_calendars options
    if request.POST and request.htmx:
        form_partial = WeekCalendarForm(data=request.POST)
        if form_partial.is_valid():
            """ main functionality changing content by date or calendar, 
            if calendar is empty all occurrences of user """
            date = form_partial.cleaned_data['date_reference']
            assert date is not None, "date should be something"
            ref_date_partial = p.datetime(date.year,date.month,date.day)
            if form_partial.cleaned_data['calendar']:
                sessions = SessionModel.objects.filter(start_datetime__week=ref_date_partial.week_of_year,
                                                            calendar=form_partial.cleaned_data['calendar']).select_related('client','client__user')
            else:
                sessions = SessionModel.objects.filter(client__user=request.user,
                                                 start_datetime__week=ref_date_partial.week_of_year).select_related('client','client__user')
            calendar_partial = CalendarRender(sessions=sessions,date_ref=ref_date_partial)
            template_calendar = template + "#calendar-view-partial"
            context = {'calendar':calendar_partial}
            return render(request,template_calendar,context)
        # There should not be errors here but just in case
        form_partial_template = template + "#form-partial"
        form_partial.fields['calendar'].queryset = room_calendar_user
        context = {'form':form_partial}
        #response for form error
        response = render(request,form_partial_template,context)
        return retarget(response,"#calendar-form-tr") # retarget if not valid, switch week table (edge cases)
    #default GET response
    form = WeekCalendarForm()
    form.fields['calendar'].queryset = room_calendar_user
    sessions = SessionModel.objects.filter(client__user=request.user,
                                           start_datetime__week=p.now().week_of_year).select_related('client','client__user')
    calendar = CalendarRender(sessions=sessions) # today by default
    context = {'calendar':calendar,'form':form}
    return render(request,template,context)

def week_view_auxiliary(request):
    clients = ClientModel.objects.filter(user=request.user)
    template = "room_calendar_app/auxiliary/client_list_li.html"
    context = {"clients":clients}
    return render(request,template,context)

def week_view_add_session_client(request,date_ref,day,time):
    if request.POST:
        form = ClientSessionForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            week_year = p.instance(date_ref).week_of_year()
            start_datetime = p.now().replace(day=day,hour=time,week=week_year)
            instance.start_datetime = start_datetime
            instance.end_datetime = instance.client.duration + start_datetime
            instance.user = request.user
            instance.save()
            messages.info(request,f"Session added for {instance.client.name}")
            return render(request,'_toasts.html')
        form = ClientSessionForm(data=request.POST)
        context = {'form':form}
        return render(request,'room_calendar_app/input/session_form_client.html',context)
        return None
    else:
        form = ClientSessionForm()
        context = {'form':form}
        return render(request,'room_calendar_app/input/session_form_client.html',context)

def week_view_add_session_date(request,date_ref,client_ref):
    if request.POST:
        form = StartDateSessionForm(data=request.POST)

def room_calendar_listing_view(request):
    room_calendar_mine = RoomCalendarModel.objects.filter(user=request.user)
    room_calendar_tenant = RoomCalendarModel.objects.filter(tenants__user=request.user)
    context = {"calendar_mine": room_calendar_mine,"calendar_tenant": room_calendar_tenant}
    return render(request,"room_calendar_app/display/room_calendar_list.html",context)

def room_calendar_view(request,calendar_pk):
    calendar = get_object_or_404(RoomCalendarModel, pk=calendar_pk,user=request.user)
    tenants = calendar.tenants.all()
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




def tenant_view(request,tenant_pk):
    tenant = get_object_or_404(TenantModel, pk=tenant_pk)
    context = {"tenant": tenant}
    return render(request,"room_calendar_app/display/tenant.html",context)


def tenant_listing_view(request):
    """View a list of user's events """
    tenant_list = TenantModel.objects.filter(user=request.user)  #? I already changed this one
    context = {"tenant_list":tenant_list}
    return render(request, "room_calendar_app/display/tenant_list.html", context) #todo check template


def room_calendar_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    if request.method !='POST':
        #no data submitted; create a blank form
        form = RoomCalendarForm()
        action = "Add"
    else:
        #POST data submitted; process data
        form = RoomCalendarForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('room_calendar_app:room_calendar_list')
    #display a blank or invalid form
    context = {'form':form,"action":action}
    return render(request,'room_calendar_app/input/add_calendar.html',context)

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


def room_calendar_edit_view(request,room_calendar_pk):
    """edit the occurrence repetition erasing future events"""
    room_calendar = RoomCalendarModel.objects.get(pk=room_calendar_pk)
    if request.method !='POST':
        action = "Edit"
        #no data submitted; create a blank form
        form = RoomCalendarForm(instance=room_calendar)
    else:
        #POST data submitted; process data
        check_owner(room_calendar.user,request.user)
        form = RoomCalendarForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_calendar_app:room_calendar_list')
    #display a blank or invalid form
    context = {'form':form,"action":action}
    return render(request,"room_calendar_app/input/add_calendar.html",context)



def tenant_edit_view(request,tenant_pk):
    """edit the occurrence repetition erasing future events"""
    tenant = TenantModel.objects.get(pk=tenant_pk)
    if request.method !='POST':
        action = "Edit"
        #no data submitted; create a blank form
        form = TenantForm(instance=tenant)
    else:
        #POST data submitted; process data
        check_owner(tenant.user,request.user)
        form = TenantForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_calendar_app:tenants')
    #display a blank or invalid form
    context = {'form':form,"action":action}
    return render(request,"room_calendar_app/input/add_tenant.html",context)

def tenant_link_view(request,calendar_pk):
    """edit the occurrence repetition erasing future events"""
    calendar = RoomCalendarModel.objects.get(pk=calendar_pk)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = LinkTenantForm()
    else:
        #POST data submitted; process data
        form = LinkTenantForm(data=request.POST)
        if form.is_valid():
            tenant_uuid = form.cleaned_data["tenant_id"]
            #calendar = RoomCalendarModel.objects.get(calendar)
            calendar.tenants.add(tenant_uuid)
            return redirect('room_calendar_app:room_calendar_list')
    #display a blank or invalid form
    context = {'form':form,"calendar":calendar}
    return render(request,"room_calendar_app/input/link_tenant.html",context)





