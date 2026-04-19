from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404

from ppm_app.responses.hx_responses import ok_response_modal, ups_response, ok_response
from room_calendar_app.models import TenantModel
from .models import ClientModel, SessionModel
from django.http import Http404, HttpResponse
from .forms import SessionForm, SessionSelectGroupForm, SearchSessionForm, SessionFromCalendarForm, \
    SelectAttendanceForm, PatchBriefForm, SessionsBulkActionsForm, SessionShortForm, ClientAndMonthForSessions
from django_htmx.http import retarget, HttpResponseClientRefresh, reswap
import pendulum as p
from django.contrib import messages
from .utils import csv_session_list_response, time_plus_duration
import logging

logger = logging.getLogger(__name__)


# Create your views here.


# * session


def sessions_view(request, client_uuid=None, add_forward=False) -> HttpResponse:
    """show open sessions, add a new simple session, update pay status with other hx-views
    it filters sessions that are open and have already passed now() -1 hour as reference.
    """
    sessions = (SessionModel.objects
                .filter(client__user=request.user, open=True)
                .order_by('-date', '-start_time'))
    clients_user = ClientModel.objects.filter(user=request.user) or ClientModel.objects.none()  # for select
    template = 'session_client/lists/session_open_list.html'
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
            template_calendar = "session_client/hx/_session_list.html" + "#session-tbody-partial"
            context = {'sessions': sessions}
            return render(request, template_calendar, context)
        # render form errors
        form_partial.fields['client'].queryset = clients_user
        template_partial = template + '#session-form-partial'
        context = {'form': form_partial}
        response = render(request, template_partial, context)
        return retarget(response, "session-form-partial")
    form = SessionSelectGroupForm()
    form.fields['client'].queryset = clients_user
    if client_uuid:
        sessions = sessions.filter(client__uuid=client_uuid)
    if not add_forward:
        sessions = sessions.filter(date__lte=p.now().date())
    context = {'sessions': sessions, 'form': form, 'select': SelectAttendanceForm}
    return render(request, template, context)


def sessions_hx_edit_paid(request, session_uuid):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        session = get_object_or_404(SessionModel, uuid=session_uuid, client__user=request.user)
        if session.paid:
            session.paid = False
        else:
            session.paid = True
        session.save()
        template = 'session_client/hx/_session_list.html#session_paid'
        context = {'session': session}
        return render(request, template, context)  # empty response that empties the li object
    raise Http404("Not a expected request")


def sessions_hx_edit_open(request, session_uuid):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        session = get_object_or_404(SessionModel, uuid=session_uuid, client__user=request.user)
        if session.open:
            session.open = False
        else:
            session.open = True
        session.save()
        template = 'session_client/hx/_session_list.html#session_open'
        context = {'session': session}
        return render(request, template, context)  # empty response that empties the li object
    raise Http404("Not a expected request")


def session_hx_item(request, session_uuid):
    if request.method == 'GET':
        session = get_object_or_404(SessionModel, client__user=request.user, uuid=session_uuid)
        template = 'session_client/item/session_modal.html'
        if request.htmx.target == "modal-body-wrapper":
            template = template + "#modal-body-partial"
        context = {'session': session}
        return render(request, template, context)
    raise Http404("Not a expected request")


def sessions_search(request, review=False):
    """ Search sessions by date and client
    Creates a CSV file from results
    Also points to a second url and HTML for client reviews
    """
    template = "session_client/lists/"
    if review:
        """ there are two routes for same Form and data """
        template += "client_review.html"
        template_hx = template + "#session-list-partial"
    else:
        template += "session_date_list.html"
        template_hx = "session_client/hx/_session_list.html" + "#session-tbody-partial"
    clients_user = ClientModel.objects.filter(user=request.user) or ClientModel.objects.none()  # for select
    if request.POST:
        form_partial = SearchSessionForm(data=request.POST)
        if form_partial.is_valid():
            start_ref = form_partial.cleaned_data['date_ref_start']
            end_ref = form_partial.cleaned_data['date_ref_end']
            client_ref = form_partial.cleaned_data['client'] or None
            sessions = SessionModel.objects.filter(date__gte=start_ref, date__lte=end_ref)
            sessions = sessions.filter(client=client_ref) if client_ref else sessions.filter(client__user=request.user)
            sessions = sessions.order_by('client', 'date', 'start_time') if review else sessions.order_by('date',
                                                                                                          'start_time')
            if request.htmx:
                context = {'sessions': sessions}
                return render(request, template_hx, context)
            return csv_session_list_response(sessions, client_ref, start_ref, end_ref)
        else:
            raise Http404(f"The form has errors: {form_partial.errors}")
    sessions = SessionModel.objects.none()  # ? loaded by htmx after load
    form = SearchSessionForm()
    form.fields['client'].queryset = clients_user
    context = {'sessions': sessions, 'form': form}
    return render(request, template, context)


def session_list_forward_modal(request, client_uuid):
    now = p.now()
    template = "session_client/lists/session_list_modal.html"
    sessions = SessionModel.objects.filter(
        client__uuid=client_uuid,
        client__user=request.user,
        date__gt=now).order_by('-date', '-start_time')
    context = {'sessions': sessions, "client_uuid": client_uuid, "forward": True}
    return render(request, template, context)


def session_pending_list_modal(request, client_uuid):
    now = p.now()
    template = "session_client/lists/session_list_modal.html"
    sessions = SessionModel.objects.filter(
        client__uuid=client_uuid,
        client__user=request.user,
        date__lte=now.date(),
        open=True).order_by('-date', '-start_time')
    context = {'sessions': sessions, "client_uuid": client_uuid}
    return render(request, template, context)


def add_session_view(request):
    """add new session"""
    template = 'session_client/edit/edit_session_modal.html'
    if request.method != 'POST':
        # no data submitted; create a blank form
        form = SessionForm()
    else:
        # POST data submitted; process data
        form = SessionForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.deduce_from_client()
            saved, overlap = instance.save_with_checks()
            if not saved:
                # template_overlap = "session_client/lists/session_overlap_modal.html"
                # response = render(request, template_overlap,{"sessions":overlap})
                # return retarget(response,"#modal-wrapper")
                return ups_response(request, _(f"ups"), "#ups-col",
                                    overlaps=overlap)  # TODO ; can i know more specific overlap??
            return ok_response_modal(request, f"Saved ok")
    # display a blank or invalid form
    context = {'form': form}
    return render(request, template, context)


def edit_session_view(request, session_uuid):
    """edit an existing Session"""
    session = get_object_or_404(SessionModel,
                                uuid=session_uuid,
                                client__user=request.user)
    template = 'session_client/edit/edit_session_modal.html'
    if request.htmx.target == "modal-body-wrapper":
        template = template + "#modal-body-partial"
    if request.method != 'POST':
        # initial request;pre-fill form with the current entry
        form = SessionForm(instance=session)
    else:
        # POST data submitted; process data
        form = SessionForm(instance=session, data=request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            saved, overlap = session.save_with_checks()
            if not saved:
                # template_overlap = "session_client/lists/session_overlap_modal.html"+"#modal-inner-partial"
                # response = render(request, template_overlap,{"sessions":overlap})
                # return retarget(response,f"#modal-{session.uuid}")
                return ups_response(request, _(f"ups"), "#ups-col",
                                    overlaps=overlap)  # TODO ; can i know more specific overlap??
            return ok_response_modal(request, _(f"Saved ok"))
        else:
            return render(request, template, {'form': form})
    context = {'session': session, 'form': form}
    return render(request, template, context)


def hx_delete_session(request, session_uuid):
    session = get_object_or_404(SessionModel, uuid=session_uuid, client__user=request.user)
    if request.method == 'DELETE':
        session.delete()
        messages.info(request, f"Session '{session.start_time.strftime('%d-%m-%y,%H:%M')}' deleted")
        return HttpResponseClientRefresh()
    messages.error(request, f"Session '{session.start_time.strftime('%d-%m-%y, %H:%M')}' not deleted")
    return render(request, '_toasts.html')


def week_view_add_session_client(request, year=None, week=None, week_day=None, time=None):
    """ to create sessions from the calendar using calendar info as base """
    template = 'room_calendar_app/input/session_form_client.html'

    if request.method == 'POST':
        form = SessionFromCalendarForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.deduce_from_client(date=False,
                                        start_time=False,
                                        tenant=False if instance.tenant else True)
            saved, overlap = instance.save_with_checks()
            if not saved:
                template_overlap = "session_client/lists/session_overlap_modal.html"
                response = render(request, template_overlap, {"sessions": overlap})
                return retarget(response, "#modal-wrapper")
            instance.save()
            messages.info(request, f"Session added for {instance.client.code}")
            return ok_response_modal(request, "Session Saved",
                                     event_and_target=("RefreshTable", "#caption-form"))
        # form errors
        template = template + '#session_calendar_form_partial'
        context = {'form': form}
        return render(request, template, context)
    # get response
    assert year is not None, "Year is required for get calls"
    assert week is not None, "Week is required for get calls"
    assert week_day is not None, "Week_day is required for get calls"
    assert time is not None, "Time is required for get calls"
    iso_week = f"{year}-W{week:02d}-{week_day}"
    date_from_iso_week = p.parse(iso_week).date()
    time_from_str = p.parse(time).time()
    data = {
        'date': date_from_iso_week,
        'start_time': time_from_str,
    }
    form = SessionFromCalendarForm(initial=data)
    client_qs = ClientModel.objects.filter(user=request.user)
    tenant_qs = TenantModel.objects.filter(user=request.user)
    form.fields['client'].queryset = client_qs
    form.fields['tenant'].queryset = tenant_qs
    context = {'form': form}
    return render(request, template, context)


def add_series_view(request, client_uuid, number):
    """add new session"""
    if request.htmx:
        date_ref = p.now()
        template = 'session_client/lists/client_list.html' + "#future_sessions_partial"
        client = get_object_or_404(ClientModel, uuid=client_uuid, user=request.user)
        success, sessions = client.add_series(number)
        if success:
            client_after = ClientModel.objects.filter(uuid=client_uuid).annotate(
                future_sessions_count=Count('sessionmodel',
                                            filter=Q(sessionmodel__date__gt=date_ref.date()))).last()
            return render(request, template, {"client": client_after})
        else:
            template_overlap = "session_client/lists/sessions_toast.html"
            response = render(request, template_overlap, {'sessions': sessions, "created": False})
            return retarget(response, "#toast-wrapper")
    return Http404("Not a expected request")


def add_copy_forward_view(request, session_uuid):
    if request.htmx:
        session = SessionModel.objects.get(uuid=session_uuid)
        new_session = SessionModel(
            date=p.instance(session.date).add(weeks=1),
            start_time=session.start_time,
            end_time=session.end_time,
            calendar=session.calendar,
            client=session.client,
            fee=session.fee,
            open=True,
            paid=False
        )
        unique, qs = new_session.is_unique()
        if unique:
            new_session.save()
            return render(request, "_ok.html")
        else:
            sessions = qs
            template = "session_client/lists/session_overlap_modal.html"
            response = render(request, template, {"sessions": sessions})
            response = reswap(response, "innerHTML")
            return retarget(response, "#modal-wrapper")
    return Http404("Ups,error on this site")


def sessions_hx_edit_attendance(request, session_uuid, attendance):
    session = get_object_or_404(SessionModel, uuid=session_uuid, client__user=request.user)
    session.attendance = attendance
    session.save()
    messages.info(request, f"Session '{session.start_time.strftime('%d-%m-%y,%H:%M')}' updated")
    template = 'session_client/hx/_session_list.html' + "#attendance_partial"
    return render(request, template, {"session": session})


def sessions_patch_attendance(request, session_uuid):
    session = get_object_or_404(SessionModel, uuid=session_uuid, client__user=request.user)
    if request.htmx:
        form = SelectAttendanceForm(data=request.POST, instance=session)
        if form.is_valid():
            session = form.save()
            messages.info(request, f"Session '{session.start_time.strftime('%d-%m-%y,%H:%M')}' updated")
            template = 'session_client/hx/_session_list.html' + "#attendance_partial"
            return render(request, template, {"session": session})
    return HttpResponse(status=404)


def patch_brief_view(request, session_uuid):
    session = get_object_or_404(SessionModel, uuid=session_uuid)
    form = PatchBriefForm(instance=session)
    if request.method == 'POST':
        form = PatchBriefForm(data=request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.debug(request, "Brief updated")
            logger.info(f"session {session}, updated")
            return HttpResponseClientRefresh()
        logger.info("form not valid")
    template = "session_client/hx/_brief.html"
    return render(request, template, {"form": form, "session": session})


def bulk_actions_hx(request):
    template = "session_client/hx/_session_list.html#bulk_form"
    form = SessionsBulkActionsForm()
    if request.method == 'POST':
        form = SessionsBulkActionsForm(request.POST)
        selected_uuids = request.POST.getlist('sessionCheckbox')
        print(request.POST)
        if form.is_valid():
            action = form.cleaned_data['actions']
            sessions = SessionModel.objects.filter(uuid__in=selected_uuids)
            match action:
                case "close":
                    rows_changed = sessions.update(open=False)
                case "open":
                    rows_changed = sessions.update(open=True)
                case "paid":
                    rows_changed = sessions.update(paid=True)
                case "unpaid":
                    rows_changed = sessions.update(paid=False)
                case "attended":
                    rows_changed = sessions.update(attendance="Attended")
                case _:
                    rows_changed = 0
            return ok_response(request, f"Updates: {rows_changed}",
                               "#bulk-response",
                               ("RefreshTable", "#session-list-form"),
                               "innerHTML")
    return render(request, template, {"bulk_form": form})


def sessions_add_set_view(request):
    clients = ClientModel.objects.filter(user=request.user, active=True)
    template = "session_client/edit/add_sessions_set.html"
    form = ClientAndMonthForSessions()
    if request.method == 'POST':
        form = ClientAndMonthForSessions(request.POST)
        if form.is_valid():
            logger.debug("form 'client and month for session is valid")
            client = form.cleaned_data['clients']
            date = form.cleaned_data['dates']
            return sessions_add_set_hx(request, client=client, date=date)
    form.fields['clients'].queryset = clients
    context = {'form': form}
    return render(request, template, context)


def sessions_add_set_hx(request, client_uuid=None, client=None, date=None, date_str=None, ):
    FormSet = inlineformset_factory(ClientModel, SessionModel,
                                    fields=['date', 'start_time', 'paid', 'attendance', 'open'],
                                    extra=5, max_num=8, can_delete=True,
                                    )
    client_instance = client if client else ClientModel.objects.get(uuid=client_uuid)
    client_instance.sort_tenant_calendar()  # gives them a tenant and room if do not have one
    date_p = p.instance(date) if date else p.from_format(date_str, 'YYYY-MM-DD')
    if request.method == 'POST':
        client_instance = client_instance
        formset = FormSet(data=request.POST, instance=client_instance,
                          queryset=SessionModel.objects.filter(date__month=date_p.month,
                                                               date__year=date_p.year, client=client_instance))
        if formset.is_valid():
            sessions = formset.save(commit=False)
            sessions = set(s for s in sessions if s.pk)
            for obj in formset.deleted_objects:
                obj.delete()
            result = "Overlaps"
            new_sessions = set()
            update_sessions = set()
            overlaps = set()
            for session in sessions:
                session.end_time = time_plus_duration(session.start_time, client_instance.duration)
                session.open = True
                session.paid = False
                session.fee = client_instance.fee
                session.tenant = client_instance.tenant
                unique, overlap = session.is_unique()
                if unique:
                    logger.info(f"sessions created: {session}")
                    if session.pk:
                        update_sessions.add(session)
                    else:
                        new_sessions.add(session)
                else:
                    overlaps.add(overlap)
            if not overlaps:
                result = _("Created")
                logger.info(f"sessions created: {len(new_sessions)}")
                logger.info(f"sessions updated: {len(update_sessions)}")
                SessionModel.objects.bulk_create(new_sessions)
                SessionModel.objects.bulk_update(update_sessions,
                                                 fields=['start_time', 'end_time', 'open', 'paid', 'date',
                                                         'attendance'])
            if overlaps:
                sessions = overlaps
            else:
                sessions = new_sessions | update_sessions
            context = {'sessions': sessions, 'result': result}
            logger.info(f"sessions overlap: {len(sessions)}")
            return render(request, 'session_client/hx/_sessions_result.html', context)
    template = 'session_client/hx/_session_set_form.html'
    formset = FormSet(instance=client_instance,
                      queryset=SessionModel.objects.filter(date__month=date_p.month,
                                                           date__year=date_p.year, client=client))
    context = {'formset': formset, 'client': client_instance, 'date': date_p.to_date_string()}
    return render(request, template, context)
