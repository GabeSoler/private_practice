import time

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from room_calendar_app.models import RoomCalendarModel, TenantModel
from .models import ClientModel, SessionModel
from django.http import Http404
from .forms import ClientForm, SearchClientForm, ClientFormShort, SearchSessionForm, ClientFromCalendarForm
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh, retarget
from django.utils import timezone
from django.contrib import messages

from .querysets import annotate_client_list
from django.contrib.postgres.search import (SearchHeadline,
                                            SearchQuery,
                                            SearchRank,
                                            SearchVector)

import pendulum as p


# Create your views here.


def clients_view(request):
    """show all clients"""
    template = 'session_client/lists/client_list.html'
    clients = annotate_client_list(request.user, active=True)
    context = {'clients': clients}
    return render(request, template, context)


def hx_client_short_form(request):
    if request.htmx:
        form = ClientFormShort()
        context = {'form': form}
        template = 'session_client/lists/client_list.html#client-form-partial'
        return render(request, template, context)
    raise Http404("Not a expected request")


def client_hx_item(request, client_uuid):
    if request.method == 'GET':
        client = get_object_or_404(ClientModel, user=request.user, uuid=client_uuid)
        template = 'session_client/item/client_modal.html'
        context = {'client': client}
        return render(request, template, context)
    raise Http404("Not a expected request")


def clients_toggle_active(request, client_uuid):
    """ manages clients htmx calls """
    if request.method == 'PATCH':
        occurrence = get_object_or_404(ClientModel, uuid=client_uuid, user=request.user)
        if occurrence.active:
            occurrence.active = False
        else:
            occurrence.active = True
        occurrence.archived_at = timezone.now()
        occurrence.save()
        messages.info(request, f"Client '{occurrence.code}' toggled")
        return HttpResponseClientRefresh()
    return HttpResponseClientRedirect(reverse("session_client:client_list"))


def client_search_view(request):
    """
    searchs through sessions based on text vectors, and organises results by clients
    """
    template = 'session_client/lists/client_search.html'
    if request.method == 'POST':
        form_partial = SearchClientForm(data=request.POST)
        if form_partial.is_valid():
            raw_query = form_partial.cleaned_data['search_input']
            search_query = SearchQuery(raw_query)
            vector_brief = SearchVector("keywords", weight="A")
            vector_calendar = SearchVector("calendar__name", weight="D")
            vector_client = SearchVector("client__code", weight="C")
            vector = (vector_client + vector_calendar + vector_brief)
            client = form_partial.cleaned_data['client']
            sessions = (SessionModel.objects
                        .filter(client__user=request.user)
                        .annotate(
                search=vector,
                rank=SearchRank(vector, search_query),
                headline=SearchHeadline("keywords", search_query),
            ).filter(search=raw_query).order_by("-rank"))
            if client:
                sessions = sessions.filter(client=client)

            if request.htmx:
                """pagination of results"""
                page_number = request.GET.get("page", 1)
                paginator = Paginator(sessions, 10)
                sessions = paginator.get_page(page_number)
                template_calendar = template + "#client-list-partial"
                context = {'sessions': sessions}
            else:
                template_calendar = template
                context = {"form": form_partial, "sessions": sessions}
            return render(request, template_calendar, context)
        else:
            if request.htmx:
                response = render(request, template, {"form": form_partial})
                return retarget(response, "form-table-wrapper")
            return render(request, template, {"form": form_partial})
    form = SearchClientForm()
    form.fields["client"].queryset = ClientModel.objects.filter(user=request.user)
    context = {'form': form}
    return render(request, template, context)


def client_archived_view(request):
    template = 'session_client/lists/client_archived_list.html'
    clients = ClientModel.objects.filter(user=request.user, active=False).order_by('code')
    context = {'clients': clients}
    return render(request, template, context)


def add_client_view(request):
    """add a new client"""
    template = 'session_client/edit/edit_client_modal.html'
    if request.htmx.target == "modal-body-wrapper":
        template = template + "#modal-body-partial"
    if request.method == 'POST':
        # POST data submitted; process data
        form = ClientForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            if request.htmx:
                return HttpResponseClientRefresh()
            return redirect('session_client:client_list')
    # display a blank or invalid form
    form = ClientForm()
    form.fields['tenant'].queryset = TenantModel.objects.filter(user=request.user)
    context = {'form': form}
    return render(request, template, context)


def edit_client_view(request, client_uuid):
    """edit an existing entry"""
    client = get_object_or_404(ClientModel,
                               uuid=client_uuid,
                               user=request.user)
    form = ClientForm(instance=client)
    form.fields['tenant'].queryset = TenantModel.objects.filter(user=request.user)
    template = 'session_client/edit/edit_client_modal.html'
    if request.htmx.target == "modal-body-wrapper":
        template = template + "#modal-body-partial"

    if request.method == 'POST':
        # POST data submitted; process data
        form = ClientForm(instance=client, data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, f"Client '{client.code}' updated")
            if request.htmx:
                return HttpResponseClientRefresh()
            return redirect('session_client:client_list')
    context = {'client': client, 'form': form}
    return render(request, template, context)


def week_view_add_client(request, weekday=None, time=None, calendar=None):
    """ to create sessions from the calendar using calendar info as base """
    template = 'session_client/edit/edit_client_modal.html'
    if request.method == 'POST':
        form = ClientForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.info(request, f"Client added: {instance.code}")
            return HttpResponseClientRefresh()
        # form errors
        template = template + '#modal-body-partial'
        context = {'form': form}
        return render(request, template, context)
    # get response
    assert weekday is not None, "Week_day is required for get calls"
    assert time is not None, "Time is required for get calls"
    form = ClientForm(initial={"day": weekday, "time": p.parse(time).time()})
    tenant_qs = TenantModel.objects.filter(user=request.user)
    if calendar:
        tenant_qs = tenant_qs.filter(calendar__uuid=calendar)
    form.fields['tenant'].queryset = tenant_qs
    context = {'form': form}
    return render(request, template, context)
