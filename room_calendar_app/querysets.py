from django.utils.functional import keep_lazy

from .models import TenantModel
from django.db.models import Q, F, Case, When,FloatField,Prefetch,Count,Sum
import pendulum as p

@keep_lazy
def tenant_annotated_qs(year,month,cal=None,user=None):
    tenants_qs = (TenantModel.objects
    .annotate(
        session_count=Count("clientmodel__sessionmodel",
                            filter=Q(clientmodel__sessionmodel__date__year=year,
                                     clientmodel__sessionmodel__date__month=month),
                            ),
        period_income=Sum('clientmodel__sessionmodel__amount_paid',
                          filter=Q(clientmodel__sessionmodel__date__year=year,
                                   clientmodel__sessionmodel__date__month=month),
                          default=0))

    .annotate(
        session_pay=Case(When(agrement="Block",then=F('blocksmodel__monthly_cost')),
            When(agrement="Percentage",
                 then=F("period_income") * F("calendar__percentage") / 100),
            default=F("calendar__cost") * F("session_count"),
            output_field=FloatField()
        )))
    if cal:
        tenants_qs = tenants_qs.filter(calendar=cal)
    if user:
        tenants_qs = tenants_qs.filter(user=user)
    return tenants_qs

@keep_lazy
def get_tenant_qs_totals(tenants_qs):
    totals = tenants_qs.aggregate(
        total_sessions=Sum("session_count"),
        total_pay=Sum("session_pay")
    )
    return totals