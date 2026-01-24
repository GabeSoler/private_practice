from django.utils.functional import keep_lazy

from .models import TenantModel
from django.db.models import (Q, F, Case,
                              When, FloatField,
                              Value, Count, Sum,
                              ExpressionWrapper,
                              DateTimeField, CharField)
import pendulum as p
from session_client.models import SessionModel
from django.db.models.functions import Concat, Cast


def tenant_annotated_qs(year, month, cal=None, user=None):
    tenants_qs = (TenantModel.objects
    .annotate(
        session_count=Count("clientmodel__sessionmodel",
                            filter=Q(clientmodel__sessionmodel__date__year=year,
                                     clientmodel__sessionmodel__date__month=month) &
                                   ~Q(clientmodel__sessionmodel__attendance="Cancel"),
                            ),
        period_income=Sum('clientmodel__sessionmodel__fee',
                          filter=Q(clientmodel__sessionmodel__date__year=year,
                                   clientmodel__sessionmodel__date__month=month) &
                                 ~Q(clientmodel__sessionmodel__attendance="Cancel"),
                          default=0))

    .annotate(
        session_pay=Case(When(agreement="Block", then=F('blocksmodel__monthly_cost')),
                         When(agreement="Percentage",
                              then=F("period_income") * F("calendar__percentage") / 100),
                         default=F("calendar__cost") * F("session_count"),
                         output_field=FloatField()
                         )))
    if cal:
        tenants_qs = tenants_qs.filter(calendar=cal)
    if user:
        tenants_qs = tenants_qs.filter(user=user)
    return tenants_qs


def get_tenant_qs_totals(tenants_qs):
    totals = tenants_qs.aggregate(
        total_sessions=Sum("session_count"),
        total_pay=Sum("session_pay"),
        total_income=Sum("period_income"),
    )
    return totals


def week_view_session_qs(request):
    sessions_qs = (SessionModel.objects
    .filter(client__user=request.user)
    .select_related('client__user')
    .exclude(attendance="Cancel")
    .annotate(
        out_display=Concat(
            F("client__tenant__display_name"),
            Value("-"),
            Cast("start_time", output_field=CharField(max_length=5)),
            Value("-"),
            Cast("end_time", output_field=CharField(max_length=5)),
            output_field=CharField()),
        in_display=Concat(
            F("client__code"),
            Value("-"),
            Cast("start_time", output_field=CharField(max_length=5)),
            Value("-"),
            Cast("end_time", output_field=CharField(max_length=5)),
            output_field=CharField()),
        display=Case(When(client__user=request.user, then=F("in_display")), default=F("out_display")),
        start_datetime=ExpressionWrapper(
            F("date") + F("start_time"),
            output_field=DateTimeField()),
        end_datetime_adjusted=ExpressionWrapper(
            F("date") + F("end_time") - p.duration(minutes=30),
            output_field=DateTimeField()),
    ))
    return sessions_qs
