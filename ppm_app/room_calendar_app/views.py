from django.shortcuts import get_object_or_404, render,redirect

from .models import Event, OccurrenceModel,RoomCalendarModel,MultiOccurrenceModel
from .forms import EventForm,MultipleOccurrenceForm
from django.shortcuts import get_object_or_404, render



def index_view(request):
    return render(request,"room_calendar_app/index.html")


def room_calendars_view(request):
    user = request.user
    room_calendar = get_object_or_404(RoomCalendarModel,user=user)
    events = Event.objects.filter(
        room_calendar=room_calendar,
        user = user)
    context = {"events": events, "room_calendar": room_calendar}
    return render(request,"room_calendar_app/index.html",context)



#! swing time from here

def event_listing(request):
    """View all ``events``."""
    events = Event.objects.all(user=request.user)  #? I already changed this one
    context = events
    return render(request, "room_calendar_app/event_list.html", context) #todo check template


def event_view(request,event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    context = {"event": event}
    return render(request,"room_calendar_app/event_list.html",context)


def event_add_view(request,room_pk):
    """ add an event, it needs to set occurrences to appear in the calendar"""
    if request.method !='POST':
        #no data submitted; create a blank form
        form = EventForm(user=request.user,room_calendar=room_pk)
    else:
        #POST data submitted; process data
        form = EventForm(data=request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.user = request.user 
            isinstance.save()
            return redirect('tools:client_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'tools/client_session/add_client.html',context)

def event_multiple_view(request,event_pk):
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

def event_multiple_edit_view(request,event_pk):
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




