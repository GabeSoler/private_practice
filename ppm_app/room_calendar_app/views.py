from django.shortcuts import get_object_or_404, render,redirect
from django.http import Http404

from .models import Event, OccurrenceModel,RoomCalendarModel,MultiOccurrenceModel,TenantModel
from .forms import EventForm,MultipleOccurrenceForm,RoomCalendarForm,TenantForm,LinkTenantForm,OccurrenceForm
from django.shortcuts import get_object_or_404, render
from tools.models import Client

def check_owner(topic_owner,request_user):
    if topic_owner != request_user:
        raise Http404
    

def index_view(request):
    return render(request,"room_calendar_app/index.html")

def week_view(request):
    return render(request,"room_calendar_app/display/calendar.html")



def room_calendar_listing_view(request):
    tenant = TenantModel.objects.filter(user=request.user)
    room_calendar_mine = RoomCalendarModel.objects.filter(user=request.user)
    room_calendar_tenant = RoomCalendarModel.objects.filter(tenants__user=request.user)
    context = {"calendar_mine": room_calendar_mine,"calendar_tenant": room_calendar_tenant}
    return render(request,"room_calendar_app/display/room_calendar_list.html",context)

def room_calendar_view(request,calendar_pk):
    calendar = get_object_or_404(RoomCalendarModel, pk=calendar_pk)
    tenants = calendar.tenants.all()
    context = {"calendar": calendar,"tenants":tenants}
    return render(request,"room_calendar_app/display/room_calendar.html",context)

def event_view(request,event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    context = {"event": event}
    return render(request,"room_calendar_app/display/event.html",context)

def tenant_view(request,tenant_pk):
    tenant = get_object_or_404(TenantModel, pk=tenant_pk)
    context = {"tenant": tenant}
    return render(request,"room_calendar_app/display/tenant.html",context)


def tenant_listing_view(request):
    """View a list of user's events """
    tenant_list = TenantModel.objects.filter(user=request.user)  #? I already changed this one
    context = {"tenant_list":tenant_list}
    return render(request, "room_calendar_app/display/tenant_list.html", context) #todo check template


def event_listing_view(request):
    """View a list of user's events """
    events = Event.objects.filter(user=request.user)  #? I already changed this one
    context = {"events":events}
    return render(request, "room_calendar_app/display/event_list.html", context) #todo check template

def occurrence_listing_view(request):
    """View all ``events``."""
    occurrences = OccurrenceModel.objects.all(user=request.user)  #? I already changed this one
    context = occurrences
    return render(request, "room_calendar_app/event_list.html", context) #todo check template

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

def event_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    if request.method !='POST':
        form = EventForm()
        form.fields["room_calendar"].queryset = RoomCalendarModel.objects.filter(tenants__user=request.user)
        form.fields["client"].queryset = Client.objects.filter(user=request.user)
    else:
        #POST data submitted; process data
        form = EventForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('room_calendar_app:event_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'room_calendar_app/input/add_event.html',context)

def occurrence_add_view(request):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    if request.method !='POST':
        #no data submitted; create a blank form
        form = OccurrenceForm()
        form.fields["event"].queryset = Event.objects.filter(user=request.user)
    else:
        #POST data submitted; process data
        form = OccurrenceForm(data=request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.user = request.user 
            isinstance.save()
            return redirect('room_calendar_app:occurrence_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'room_calendar_app/input/add_occurrence.html',context)

def occurrence_multiple_add_view(request,event_pk):
    """ loads a multiple form and creates the events"""
    event = Event.objects.get(pk=event_pk)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = MultipleOccurrenceForm()
    else:
        #POST data submitted; process data
        form = MultipleOccurrenceForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.event = event
            instance.save()
            multi = MultiOccurrenceModel.objects.get(instance)
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
    event = Event.objects.get(pk=event_pk)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = EventForm(instance=event)
    else:
        #POST data submitted; process data
        check_owner(event.user,request.user)
        form = EventForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_calendar_app:events')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,"room_calendar_app/input/add_event.html",context)

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
    multiple = MultiOccurrenceModel.objects.get(event=event)
    if request.method !='POST':
        #no data submitted; create a blank form
        form = MultipleOccurrenceForm(instance=multiple)
    else:
        #POST data submitted; process data
        form = MultipleOccurrenceForm(data=request.POST)
        if form.is_valid():
            form.save()
            multi = MultiOccurrenceModel.objects.get(form)
            multi.clean_upcoming()
            multi.add_occurrences()
            return redirect('room_calendar_app:events')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,"room_calendar_app/event_detail.html",context)




