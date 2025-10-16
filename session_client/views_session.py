from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import ClientModel, SessionModel
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .forms import SessionForm, SessionSelectGroupForm, SearchSessionFrom, SessionFromCalendarForm
from django_htmx.http import retarget, HttpResponseClientRedirect, HttpResponseClientRefresh,trigger_client_event
import pendulum as p
from django.contrib import messages

from .utils import time_plus_duration


# Create your views here.

def index_view(request):
    """show all session_client"""
    return render(request, 'session_client/index.html')


# * session

@login_required
def sessions_view(request,client_pk=None,add_forward=False) -> HttpResponse:
    """show open sessions, add a new simple session, update pay status with other hx-views
    it filters sessions that are open and have already passed now() -1 hour as reference.
    """
    sessions = SessionModel.objects.filter(client__user=request.user, open=True).order_by('-date', '-start_time')
    clients_user = ClientModel.objects.filter(user=request.user) or None  # for select
    template = 'session_client/lists/session_open_list.html'
    form = SessionSelectGroupForm()
    if request.htmx:
        form_partial = SessionSelectGroupForm(data=request.POST)
        if form_partial.is_valid():
            only_unpaid = form_partial.cleaned_data['only_unpaid']
            include_next = form_partial.cleaned_data['include_next']
            client = form_partial.cleaned_data['client']
            if only_unpaid:
                sessions = sessions.filter(paid=False)
            if not include_next:
                sessions = sessions.filter(date__lte=p.now().date())
            if client:
                sessions = sessions.filter(client=client)
            template_calendar = "session_client/navs/session-nav.html" + "#session-list-partial"
            context = {'sessions': sessions}
            return render(request, template_calendar, context)
        # render form errors
        template_partial = template + '#session-form-partial'
        context = {'form': form_partial}
        response = render(request, template_partial, context)
        return retarget(response, "session-form-partial")
    form.fields['client'].queryset = clients_user
    if client_pk:
        sessions = sessions.filter(client__pk=client_pk)
    if not add_forward:
        sessions = sessions.filter(date__lte=p.now().date())
    context = {'sessions': sessions, 'form': form}
    return render(request, template, context)


@login_required
def sessions_hx_edit_paid(request, session_pk):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        session = get_object_or_404(SessionModel, pk=session_pk, client__user=request.user)
        if session.paid:
            session.paid = False
        else:
            session.paid = True
        session.save()
        template = 'session_client/navs/session-nav.html#session_paid'
        context = {'session': session}
        return render(request, template, context)  # empty response that empties the li object
    raise Http404("Not a expected request")


@login_required
def sessions_hx_edit_open(request, session_pk):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        session = get_object_or_404(SessionModel, pk=session_pk, client__user=request.user)
        if session.open:
            session.open = False
        else:
            session.open = True
        session.save()
        template = 'session_client/navs/session-nav.html#session_open'
        context = {'session': session}
        return render(request, template, context)  # empty response that empties the li object
    raise Http404("Not a expected request")


def session_hx_item(request, session_pk):
    if request.method == 'GET':
        session = get_object_or_404(SessionModel, client__user=request.user, pk=session_pk)
        template = 'session_client/item/session_modal.html'
        if request.htmx.target == "modal-body-wrapper":
            template = template + "#modal-body-partial"
        context = {'session': session}
        return render(request, template, context)
    raise Http404("Not a expected request")


@login_required
def sessions_search(request):
    """ Search sessions by date and client """
    template = "session_client/lists/session_date_list.html"
    clients_user = ClientModel.objects.filter(user=request.user) or None  # for select
    if request.POST:
        form_partial = SearchSessionFrom(data=request.POST)
        if form_partial.is_valid():
            start_ref = form_partial.cleaned_data['date_ref_start']
            end_ref = form_partial.cleaned_data['date_ref_end']
            client_ref = form_partial.cleaned_data['client'] or None
            if client_ref:
                # using session date as reference and csv generation.
                sessions = SessionModel.objects.filter(date__gte=start_ref,
                                                       date__lte=end_ref,
                                                       client=client_ref).order_by('date', 'start_time')
            else:
                sessions = SessionModel.objects.filter(client__user=request.user,
                                                       date__gte=start_ref,
                                                       date__lte=end_ref, ).order_by('date', 'start_time')
            if request.htmx:
                template_calendar = "session_client/navs/session-nav.html" + "#session-list-partial"
                context = {'sessions': sessions}
                return render(request, template_calendar, context)
            import csv
            start_ref_str = p.instance(start_ref).to_formatted_date_string()  # converting for easier formatting
            end_ref_str = p.instance(end_ref).to_formatted_date_string()
            file_name = f"{client_ref}: {start_ref_str}-{end_ref_str}" if client_ref else f"{start_ref_str}-{end_ref_str}"
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{file_name}.csv"'})
            fieldnames = ["date", "start_time", "client", "brief", "paid"]
            writer = csv.writer(response)  # response is the output
            writer.writerow(fieldnames)
            for row in sessions:
                writer.writerow([row.date, row.start_time, row.client, row.brief, row.paid])
            return response

        else:
            raise Http404(f"The form has errors: {form_partial.errors}")
    sessions = SessionModel.objects.none()  # ? loaded by htmx after load
    form = SearchSessionFrom()
    form.fields['client'].queryset = clients_user
    context = {'sessions': sessions, 'form': form}
    return render(request, template, context)

@login_required()
def session_list_forward_modal(request, client_pk):
    now = p.now()
    template = "session_client/lists/session_list_modal.html"
    sessions = SessionModel.objects.filter(
        client=client_pk,
        client__user=request.user,
        date__gte=now).order_by('-date', '-start_time')
    context = {'sessions': sessions,"client_pk":client_pk,"forward":True}
    return render(request, template, context)

@login_required()
def session_pending_list_modal(request, client_pk):
    now = p.now()
    template = "session_client/lists/session_list_modal.html"
    sessions = SessionModel.objects.filter(
        client=client_pk,
        client__user=request.user,
        date__lte=now.date(),
        open=True).order_by('-date', '-start_time')
    context = {'sessions': sessions,"client_pk":client_pk}
    return render(request, template, context)


@login_required
def add_session_view(request):
    """add new session"""
    if request.htmx:
        template = 'session_client/edit/edit_session_modal.html'
    else:
        template = 'session_client/edit/edit_session.html'
    if request.method != 'POST':
        # no data submitted; create a blank form
        form = SessionForm()
    else:
        # POST data submitted; process data
        form = SessionForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.deduce_from_client()
            instance.save()
            if request.htmx:
                return HttpResponseClientRefresh()
            return redirect('session_client:session_list')
    # display a blank or invalid form
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_session_view(request, session_pk):
    """edit an existing Session"""
    session = get_object_or_404(SessionModel,
                                pk=session_pk,
                                client__user=request.user)
    if request.htmx:
        template = 'session_client/edit/edit_session_modal.html'
        if request.htmx.target == "modal-body-wrapper":
            template = template + "#modal-body-partial"
    else:
        template = 'session_client/edit/edit_session.html'
    if request.method != 'POST':
        # initial request;pre-fill form with the current entry
        form = SessionForm(instance=session)
    else:
        # POST data submitted; process data
        form = SessionForm(instance=session, data=request.POST)
        if form.is_valid():
            session = form.save()
            messages.info(request, f"Session '{session.brief}' updated")
            return HttpResponseClientRefresh()
        else:
            messages.error(request, form.errors)
            return render(request, template, {"form": form, "session": session})
    context = {'session': session, 'form': form}
    return render(request, template, context)


@login_required
def hx_delete_session(request, session_pk):
    session = get_object_or_404(SessionModel, pk=session_pk, client__user=request.user)
    if request.method == 'DELETE':
        session.delete()
        messages.info(request, f"Session '{session.start_time.strftime('%d-%m-%y,%H:%M')}' deleted")
        return HttpResponseClientRefresh()
    messages.error(request, f"Session '{session.start_time.strftime('%d-%m-%y, %H:%M')}' not deleted")
    return render(request, '_toasts.html')


@login_required
def week_view_add_session_client(request, year=None, week=None, week_day=None, time=None, calendar=None):
    """ to create sessions from the calendar using calendar info as base """
    template = 'room_calendar_app/input/session_form_client.html'
    if request.method == 'POST':
        form = SessionFromCalendarForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.deduce_from_client(date=False,
                                        start_time=False,
                                        calendar=False if instance.calendar else True)
            instance.save()
            messages.info(request, f"Session added for {instance.client.code}")
            return HttpResponseClientRefresh()
        # form errors
        template = template + '#session_calendar_form_partial'
        context = {'form': form}
        return render(request, template, context)
    # get response
    assert year is not None, "Year is required for get calls"
    assert week is not None, "Week is required for get calls"
    assert week_day is not None, "Week_day is required for get calls"
    assert time is not None, "Time is required for get calls"
    iso_week = f"{year}-W{week}-{week_day}"
    date_from_iso_week = p.parse(iso_week).date()
    time_from_str = p.parse(time).time()
    data = {
        'date': date_from_iso_week,
        'start_time': time_from_str,
        'calendar': calendar or None,
    }
    form = SessionFromCalendarForm(data=data)
    context = {'form': form}
    return render(request, template, context)

@login_required()
def add_series_view(request,client_pk,number):
    """add new session"""
    if request.htmx:
        date_ref = p.now()
        template = 'session_client/lists/client_list.html'+"#future_sessions_partial"
        client = get_object_or_404(ClientModel,pk=client_pk,user=request.user)
        success, sessions = client.add_series(number)
        if success:
            messages.info(request, f"✅{len(sessions)} Sessions added for {client.code}")
        else:
            messages.error(request, f"‼️{len(sessions)} overlying Sessions for {client.code}")
        client_after = ClientModel.objects.filter(pk=client_pk,user=request.user).annotate(future_sessions_count=Count('sessionmodel',
                                    filter=Q(sessionmodel__date__gt=date_ref.date()))).first()
        return render(request,template,{"client":client_after,'add_toast':True})
    return Http404("Not a expected request")

@login_required()
def sessions_hx_edit_attendance(request,session_pk,attendance):
    session = get_object_or_404(SessionModel, pk=session_pk, client__user=request.user)
    session.attendance = attendance
    session.save()
    messages.info(request, f"Session '{session.start_time.strftime('%d-%m-%y,%H:%M')}' updated")
    template = 'session_client/navs/session-nav.html'+ "#attendance_partial"
    return render(request, template, {"session": session})
