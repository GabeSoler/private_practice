from django.shortcuts import render, get_object_or_404
from django_htmx.http import HttpResponseClientRefresh
import pendulum as p

from room_calendar_app.models import TenantModel
from .forms import TimeForm, TimeClientSetForm
from .models import ClientTimes, ClientModel
from django.forms import modelformset_factory, inlineformset_factory


def edit_time(request, time_pk):
    template = 'session_client/edit/edit_time.html'
    time = get_object_or_404(ClientTimes, pk=time_pk)
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


# todo create the manage times from clients!
def manage_times(request, client_uuid):
    template = 'session_client/edit/manage_times.html'
    client = get_object_or_404(ClientModel, uuid=client_uuid)
    tenant_qs = TenantModel.objects.filter(user=request.user)
    FormSet = inlineformset_factory(ClientModel, ClientTimes,
                                    fields=["day", "time", "tenant"],
                                    extra=4, max_num=6,
                                    )
    initial = [{"tenant": client.pk} for _ in range(5) if client.pk]
    formset = FormSet(instance=client, initial=initial)
    if request.method == 'POST':
        form = FormSet(request.POST, instance=client, initial=initial)
        if form.is_valid():
            form.save()
            return HttpResponseClientRefresh()
    for form in formset.forms:
        form.fields["tenant"].queryset = tenant_qs
    return render(request, template, {'formset': formset, "client": client})
