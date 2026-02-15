from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.utils.translation import gettext_lazy as _
from django_htmx.http import retarget, HttpResponseClientRefresh, trigger_client_event, reswap
import pendulum as p
from .forms import TimeForm, TimeClientSetForm
from .models import ClientTimes
from django.forms import modelformset_factory


def edit_time(request, time_pk):
    template = 'session_client/edit/edit_time.html'
    time = get_object_or_404(ClientTimes, pk=time_pk)
    if request.method == 'POST':
        form = TimeForm(request.POST, instance=time)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
    form = TimeForm(instance=time)
    context = {'form': form}
    return render(request, template, context)


def add_time(request, time=None, week_day=None):
    template = 'session_client/edit/edit_time.html'
    if request.method == 'POST':
        form = TimeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
    form = TimeForm()
    if week_day:
        form = TimeForm(initial={"day": week_day, "time": p.parse(time).time()})
    context = {'form': form}
    return render(request, template, context)


def manage_times(request, client_pk):
    template = 'session_client/edit/manage_times.html'
    FormSet = modelformset_factory(ClientTimes, fields=["day", "time", "tenant"], extra=5)
    formset = FormSet(queryset=ClientTimes.objects.filter(client_pk=client_pk))
    if request.method == 'POST':
        form = TimeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
    return render(request, template, {'formset': formset})
