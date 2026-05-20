from django.shortcuts import render, get_object_or_404
from django_htmx.http import HttpResponseClientRefresh
import pendulum as p

from ppm_app.responses.hx_responses import ok_response_render
from room_calendar_app.models import TenantModel
from .forms import TimeAddForm, TimeEditForm
from .models import ClientTimes, ClientModel
from django.forms import inlineformset_factory

from .querysets import annotate_client_list
import logging

logger = logging.getLogger(__name__)


def edit_time(request, time_pk):
    logger.debug("Edit time called")
    template = 'session_client/edit/edit_time.html'
    time = get_object_or_404(ClientTimes, pk=time_pk)
    tenant_qs = TenantModel.objects.filter(user=request.user)
    form = TimeEditForm(instance=time)
    form.fields["tenant"].queryset = tenant_qs
    if request.method == 'POST':
        form = TimeEditForm(request.POST, instance=time)
        if form.is_valid():
            logger.debug("form edit_time::TimeEditForm is valid")
            form.save()
            return HttpResponseClientRefresh()
        logger.debug(f"form TimeFrom is not valid: {form.errors}")
        template += "#times-form-partial"
    context = {'form': form, "time": time}
    return render(request, template, context)


def add_time(request, week_day, time):
    logger.debug("Add time called")
    template = 'session_client/edit/edit_time.html'
    tenant_qs = TenantModel.objects.filter(user=request.user)
    client_qs = ClientModel.objects.filter(user=request.user)
    initial = {"day": week_day - 1, "time": p.parse(time).time()}
    form = TimeAddForm(initial=initial)
    if request.method == 'POST':
        form = TimeAddForm(request.POST, initial)
        if form.is_valid():
            logger.debug("form add_time::TimeAddForm is valid")
            new_time = form.save()
            logger.debug(f"form add_time::TimeAddForm is saved: {new_time}")
            return HttpResponseClientRefresh()
        logger.debug(f"form TimeFrom is not valid: {form.errors}")
        template += "#times-form-partial"
    form.fields["tenant"].queryset = tenant_qs
    form.fields["client"].queryset = client_qs
    context = {'form': form, "time_ref": time, "week_day": week_day}
    return render(request, template, context)


# todo create the manage times from clients!
def manage_times(request, client_uuid):
    template = 'session_client/edit/manage_times.html'
    client = get_object_or_404(ClientModel, uuid=client_uuid)
    tenant_qs = TenantModel.objects.filter(user=request.user)
    FormSet = inlineformset_factory(ClientModel, ClientTimes,
                                    fields=["day", "time", "tenant", "fortnight"],
                                    extra=1, max_num=6,
                                    )
    initial = [{"tenant": client.tenant} for _ in range(5) if client.pk]
    if request.method == 'POST':
        formset = FormSet(request.POST, instance=client, initial=initial)
        if formset.is_valid():
            formset.save()
            client = annotate_client_list(request.user).filter(pk=client.pk).first()
            partial_template = "session_client/lists/client_list.html" + "#client-card-partial"
            context = {'client': client}
            return ok_response_render(request, partial_template, context,
                                      f"#card-{client.uuid}", ("CloseModal", ".modal"),
                                      "outerHTML")
        else:
            for form in formset.forms:
                form.fields["tenant"].queryset = tenant_qs
            template += "#modal-body-partial"
            return render(request, template, {'formset': formset, "client": client})
    else:
        formset = FormSet(instance=client, initial=initial)
        for form in formset.forms:
            form.fields["tenant"].queryset = tenant_qs
        return render(request, template, {'formset': formset, "client": client})
