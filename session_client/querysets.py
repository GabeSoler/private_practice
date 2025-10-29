from django.db.models import Sum, Count, Q, Case, Avg, When, FloatField, ExpressionWrapper, F
from django.utils import timezone

from session_client.models import ClientModel
import pendulum as p

def annotate_client_list(user, active=True):
    """
    Returns a queryset of clients with common annotations.
    The queryset is lazy and won't hit the database until evaluated.
    """
    date_ref = p.now()
    three_months_ago = date_ref.subtract(months=3).date()

    return ClientModel.objects.filter(
        user=user,
        active=active
    ).annotate(
        total_payments=Sum('sessionmodel__amount_paid'),
        total_sessions=Count('sessionmodel'),
        month_sessions_paid=Sum(
            'sessionmodel__amount_paid',
            filter=Q(
                sessionmodel__date__gte=date_ref.subtract(days=30).date(),
                sessionmodel__date__lte=date_ref.date(),
                sessionmodel__paid=True
            )
        ),
        month_sessions_expected=Sum(
            'sessionmodel__amount_paid',
            filter=Q(
                sessionmodel__date__gte=date_ref.subtract(days=30).date(),
                sessionmodel__date__lte=date_ref.date(),
            ),exclude=Q(sessionmodel__attendance__exact="Cancel")
        ),
        pending_sort_sessions=Count(
            'sessionmodel',
            filter=Q(
                sessionmodel__date__lte=date_ref.date(),
                sessionmodel__open=True
            )
        ),
        future_sessions_count=Count(
            'sessionmodel',
            filter=Q(sessionmodel__date__gt=date_ref.date())
        ),
        month_sessions_count=Count(
            'sessionmodel',
            filter=Q(
                sessionmodel__date__year=date_ref.year,
                sessionmodel__date__month=date_ref.month
            )
        ),
        attendance_rate=Avg(
            Case(
                When(sessionmodel__attendance='Attended', then=1),
                When(sessionmodel__attendance='', then=None),
                default=0,
                output_field=FloatField()
            ),
            filter=Q(sessionmodel__date__gte=three_months_ago,sessionmodel__date__lte=date_ref.date())
        ),
        attendance_percentage=ExpressionWrapper(
            F('attendance_rate') * 100,
            output_field=FloatField()
        )
    )