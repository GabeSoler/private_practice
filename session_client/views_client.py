from email.policy import default

from django.db.models import Q, Avg, Case, When, FloatField, ExpressionWrapper, F
from django.db.models.aggregates import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import ClientModel
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .forms import ClientForm, SearchClientForm, ClientFormShort
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from django.utils import timezone
from django.contrib import messages
import pendulum as p

from .querysets import annotate_client_list


# Create your views here.


@login_required
def clients_view(request):
    """show all clients"""
    template = 'session_client/lists/client_list.html'
    date_ref = p.instance(timezone.now())
    clients = annotate_client_list(request.user,active=True)
    context = {'clients': clients}
    return render(request, template, context)


@login_required
def hx_client_short_form(request):
    if request.htmx:
        form = ClientFormShort()
        context = {'form': form}
        template = 'session_client/lists/client_list.html#client-form-partial'
        return render(request, template, context)
    raise Http404("Not a expected request")


@login_required
def client_hx_item(request, client_pk):
    if request.method == 'GET':
        client = get_object_or_404(ClientModel, user=request.user, pk=client_pk)
        template = 'session_client/item/client_modal.html'
        context = {'client': client}
        return render(request, template, context)
    raise Http404("Not a expected request")


@login_required
def clients_toggle_active(request, client_pk):
    """ manages clients htmx calls """
    if request.method == 'PATCH':
        occurrence = get_object_or_404(ClientModel, pk=client_pk, user=request.user)
        if occurrence.active:
            occurrence.active = False
        else:
            occurrence.active = True
        occurrence.archived_at = timezone.now()
        occurrence.save()
        messages.info(request, f"Client '{occurrence.code}' toggled")
        return HttpResponseClientRedirect(reverse("session_client:session_hx_item"), args=(client_pk,))
    return HttpResponseClientRedirect(reverse("session_client:client_list"))


@login_required
def client_search_view(request):
    template = 'session_client/lists/client_search.html'
    if request.htmx:
        form_partial = SearchClientForm(data=request.POST)
        if form_partial.is_valid():
            search_input = form_partial.cleaned_data['search_input']
            active = form_partial.cleaned_data['active']
            clients = ClientModel.objects.filter(code__icontains=search_input,
                                                 active=active,
                                                 )
            template_calendar = template + "#client-list-partial"
            context = {'clients': clients}
            return render(request, template_calendar, context)
        else:
            raise Http404(f"The form has errors: {form_partial.errors}")
    clients = ClientModel.objects.none()  # ? loaded by htmx after load
    form = SearchClientForm()
    context = {'clients': clients, 'form': form}
    return render(request, template, context)


@login_required
def client_archived_view(request):
    template = 'session_client/lists/client_archived_list.html'
    clients = ClientModel.objects.filter(user=request.user, active=False).order_by('code')
    context = {'clients': clients}
    return render(request, template, context)


@login_required
def add_client_view(request):
    """add a new client"""
    if request.htmx:
        template = 'session_client/edit/edit_client_modal.html'
        if request.htmx.target == "modal-body-wrapper":
            template = template + "#modal-body-partial"
    else:
        template = 'session_client/edit/edit_client.html'
    if request.method != 'POST':
        # no data submitted; create a blank form
        form = ClientForm()
    else:
        # POST data submitted; process data
        form = ClientForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            if request.htmx:
                return HttpResponseClientRedirect(request.htmx.current_url)
            return redirect('session_client:client_list')
    # display a blank or invalid form
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_client_view(request, client_pk):
    """edit an existing entry"""
    client = get_object_or_404(ClientModel,
                               pk=client_pk,
                               user=request.user)
    if request.htmx:
        template = 'session_client/edit/edit_client_modal.html'
        if request.htmx.target == "modal-body-wrapper":
            template = template + "#modal-body-partial"
    else:
        template = 'session_client/edit/edit_client.html'
    if request.method != 'POST':
        # initial request;pre-fill form with the current entry
        form = ClientForm(instance=client)
    else:
        # POST data submitted; process data
        form = ClientForm(instance=client, data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, f"Client '{client.code}' updated")
            if request.htmx:
                return HttpResponseClientRedirect(request.htmx.current_url)
            return redirect('session_client:client_list')
    context = {'client': client, 'form': form}
    return render(request, template, context)
