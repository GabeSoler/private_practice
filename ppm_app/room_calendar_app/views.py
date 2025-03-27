from django.shortcuts import get_object_or_404, render,redirect
from django.http import Http404,HttpResponse

from .models import Event, OccurrenceModel,RoomCalendarModel,TenantModel
from .forms import EventForm,RoomCalendarForm,TenantForm,LinkTenantForm,OccurrenceForm,OccurrenceProxyForm,WeekCalendarForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers
import datetime as dt
from django.utils import timezone
from django_htmx.http import retarget
from .calendar_utils import CalendarRender
from django.contrib import messages
import pendulum as p

def check_owner(topic_owner,request_user):
    if topic_owner != request_user:
        raise Http404
    
@login_required
def index_view(request):
    events = Event.objects.filter(user=request.user).order_by('-event_type')
    event_form = EventForm()
    context = {"events":events,'event_form':event_form}
    return render(request,"room_calendar_app/index.html",context)



@login_required
@cache_control(max_age=300)
@vary_on_headers("HX-Request")
def week_view(request):
    template = "room_calendar_app/dynamic/week_view.html"
    room_calendar_user = RoomCalendarModel.objects.filter(tenants__user=request.user) #filter room_calendars options
    if request.htmx:
        form_partial = WeekCalendarForm(data=request.POST)
        if form_partial.is_valid():
            date = form_partial.cleaned_data['date_reference']
            assert date is not None, "date should be something"
            ref_date_partial = p.datetime(date.year,date.month,date.day)
            if form_partial.cleaned_data['calendar']:
                assert form_partial.cleaned_data['calendar'] is not None,"Not passed calendar to fx"
                occurrences = OccurrenceModel.objects.filter(start_time__week=ref_date_partial.week_of_year,
                                                            calendar=form_partial.cleaned_data['calendar'])
            else:
                occurrences = OccurrenceModel.objects.filter(event__user=request.user,
                                                 start_time__week=ref_date_partial.week_of_year)
            calendar_partial = CalendarRender(occurrences=occurrences,date_ref=ref_date_partial)
            template_calendar = template + "#calendar-view-partial"
            context = {'calendar':calendar_partial}
            return render(request,template_calendar,context)
        form_partial_template = template + "#form-partial" #form re render if invalid
        form_partial.fields['calendar'].queryset = room_calendar_user
        context = {'form':form_partial}
        assert form_partial.is_valid is True,"the form must be valid (if secure)"
        response = render(request,form_partial_template,context)
        return retarget(response,"#calendar-form-tr") # retarget if valid switch week table
    ref_date = timezone.now()
    ref_date = p.instance(ref_date)
    occurrences = OccurrenceModel.objects.filter(event__user=request.user,
                                                 start_time__week=ref_date.week_of_year)
    form = WeekCalendarForm()
    form.fields['calendar'].queryset = room_calendar_user
    calendar = CalendarRender(occurrences=occurrences,date_ref=ref_date) #request when no htmx today by default
    context = {'calendar':calendar,'form':form}
    return render(request,template,context)



def room_calendar_listing_view(request):
    tenant = TenantModel.objects.filter(user=request.user)
    room_calendar_mine = RoomCalendarModel.objects.filter(user=request.user)
    room_calendar_tenant = RoomCalendarModel.objects.filter(tenants__user=request.user)
    context = {"calendar_mine": room_calendar_mine,"calendar_tenant": room_calendar_tenant}
    return render(request,"room_calendar_app/display/room_calendar_list.html",context)

@cache_control(max_age=300)
@vary_on_headers("HX-Request")
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

@cache_control(max_age=300)
@vary_on_headers("HX-Request")
def event_occurrence_view(request,event_pk):
    """ Explore an event next occurrences and add new ones"""
    now = timezone.now()
    template = 'room_calendar_app/dynamic/event.html'
    event = get_object_or_404(Event, pk=event_pk)
    occurrences = OccurrenceModel.objects.filter(event=event,start_time__gte=now).order_by('-start_time') #filter events to user
    form = OccurrenceProxyForm()
    if request.htmx:
        #htmx request triggers save and refresh of occurrences and refreshes form when errors
        form = OccurrenceProxyForm(data=request.POST)
        form_template = template + "#occurrence-form"
        if form.is_valid():
            start_date_form  = form.cleaned_data['start_date'] #datetime
            start_time_form  = form.cleaned_data['start_time'] #time object
            duration_form  = form.cleaned_data['duration'] #time difference
            start_time_add = dt.datetime.combine(start_date_form,start_time_form)
            end_time_add = start_time_add + duration_form
            occurrence,_ = OccurrenceModel.objects.get_or_create(
                duration=duration_form,
                start_time=start_time_add,
                end_time=end_time_add,
                event=event,
                calendar = event.room_calendar  # I am spiting the room into two sources, 
                                                # one by default from event and one editable for 'rare' cases
                )
            occurrence.save()
            list_template = template + '#occurrence-list'
            context = {"occurrences":occurrences}
            response = render(request,list_template,context)
            return retarget(response,'#occurrence-list-wrap') # target list if valid
        context = {'form':form,'event':event}
        return render(request,form_template,context) # change form if invalid
    #else display full page
    context = {'form':form,"event":event,"occurrences":occurrences}
    return render(request,template,context)

def edit_occurrence_list(request,occurrence_pk):
    if request.method == 'DELETE':
        occurrence = OccurrenceModel.objects.get(pk=occurrence_pk)
        occurrence.delete()
        return HttpResponse() # empty response that empties the li object


def tenant_view(request,tenant_pk):
    tenant = get_object_or_404(TenantModel, pk=tenant_pk)
    context = {"tenant": tenant}
    return render(request,"room_calendar_app/display/tenant.html",context)


def tenant_listing_view(request):
    """View a list of user's events """
    tenant_list = TenantModel.objects.filter(user=request.user)  #? I already changed this one
    context = {"tenant_list":tenant_list}
    return render(request, "room_calendar_app/display/tenant_list.html", context) #todo check template

@cache_control(max_age=300)
@vary_on_headers("HX-Request")
def event_listing_view(request):
    """View a list of user's events """
    events = Event.objects.filter(user=request.user).order_by('-created_at')  #? I already changed this one
    template =  "room_calendar_app/dynamic/event_list.html"
    form = EventForm()
    if request.htmx:
        #htmx request triggers save and refresh of occurrences and refreshes form with errors
        form = EventForm(data=request.POST)
        form_event_template = template + "#event-form"
        if form.is_valid():
            occurrence = form.save(commit=False)
            occurrence.user = request.user
            occurrence.save()
            list_template = template + '#event-list'
            context = {"events":events} # context for valid form
            response = render(request,list_template,context)
            return retarget(response,'#event-list-wrap')
        context = {'form':form} # context for invalid form
        return render(request,form_event_template,context)
    context = {"events":events,'form':form}     # context for empty form
    return render(request, template, context) #todo check template

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

def occurrence_multiple_add_view(request,event_pk):
    """ loads a multiple form and creates the events"""
    event = Event.objects.get(pk=event_pk)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = OccurrenceProxyForm()
    else:
        #POST data submitted; process data
        form = OccurrenceProxyForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            multi = None #!change
            multi.add_occurrences()
            return redirect('room_calendar_app:events')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,"room_calendar_app/event_detail.html",context)

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

def event_edit_view(request,event_pk):
    """edit the occurrence repetition erasing future events"""
    user = request.user
    events = Event.objects.filter(user=user)
    event = get_object_or_404(Event,pk=event_pk,user=user)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = EventForm(instance=event)
    else:
        #POST data submitted; process data
        form = EventForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = event.user
            instance.save()
            messages.info(request,"Event Updated")
            return redirect('room_calendar_app:event_list')
    #display a blank or invalid form
    context = {'form':form,'event':event,'events':events}
    return render(request,"room_calendar_app/dynamic/event_edit.html",context)

def occurrence_edit_view(request,occurrence_pk):
    """edit the occurrence repetition erasing future events"""
    event = OccurrenceModel.objects.get(pk=occurrence_pk)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = OccurrenceForm(instance=event)
    else:
        #POST data submitted; process data
        check_owner(event.user,request.user)
        form = OccurrenceForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_calendar_app:occurrence_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,"room_calendar_app/input/add_occurrence.html",context)

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
        action = "Edit"
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

def occurrence_multiple_edit_view(request,event_pk):
    """edit the occurrence repetition erasing future events"""
    event = Event.objects.get(pk=event_pk)
    multiple = None  #!change
    if request.method !='POST':
        #no data submitted; create a blank form
        form = OccurrenceProxyForm(instance=multiple)
    else:
        #POST data submitted; process data
        form = OccurrenceProxyForm(data=request.POST)
        if form.is_valid():
            form.save()
            multi = None #!change
            multi.clean_upcoming()
            multi.add_occurrences()
            return redirect('room_calendar_app:events')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,"room_calendar_app/event_detail.html",context)




