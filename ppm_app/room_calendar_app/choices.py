from datetime import datetime, date, time, timedelta
from django.utils.translation import gettext_lazy as _
import pendulum as p

def time_slot_options():
    """
Creats a list of time options from 8 to 21 every 15 min
    """

    interval = timedelta(minutes=30)
    start_time = time(hour=8)
    end_delta = timedelta(hours=13)
    format = "%I:%M %p"
    dt = datetime.combine(date.today(), time(0))
    dt_start = datetime.combine(dt.date(), start_time)
    dt_end = dt_start + end_delta
    options = []

    while dt_start <= dt_end:
        options.append((str(dt_start.time()), dt_start.strftime(format)))
        dt_start += interval

    return options



default_timeslot_options = time_slot_options()


def time_slots()->list:
    """ Creates a list with time slots from 8 am to 10 pm every 15 minutes """
    time_slots = []
    for x in range(80,220,5):
        hour = x//10 #divisino without residual ?
        minute = x%10*6 #residual,if 5 multiplies to get 30
        slot = time(hour=hour,minute=minute) #creates multiple choices for a time select
        time_slots.append(slot)
    return time_slots




def duration_times()->list:
    """ Creates a list of durations """
    return (
            str(timedelta(minutes=30)),
            str(timedelta(hours=1)),
            str(timedelta(minutes=90)),
            str(timedelta(hours=2)),
            str(timedelta(hours=3)),
            str(timedelta(hours=4)),
            )


def duration_times_as_dt()->list:
    return (
            timedelta(minutes=30),
            timedelta(hours=1),
            timedelta(minutes=90),
            timedelta(hours=2),
            timedelta(hours=3),
            timedelta(hours=4),
            )

EVENT_TYPE = [
    ("client", "Client Session"),
    ("super", "Supervision"),
    ("Admin", "Admin"),
    ("Processing", "Processing"),
    ("CPD", "CPD"),
]


WEEKDAY_SHORT = (
    (7, _("Sun")),
    (1, _("Mon")),
    (2, _("Tue")),
    (3, _("Wed")),
    (4, _("Thu")),
    (5, _("Fri")),
    (6, _("Sat")),
)

WEEKDAY_LONG = (
    (7, _("Sunday")),
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
)

MONTH_LONG = (
    (1, _("January")),
    (2, _("February")),
    (3, _("March")),
    (4, _("April")),
    (5, _("May")),
    (6, _("June")),
    (7, _("July")),
    (8, _("August")),
    (9, _("September")),
    (10, _("October")),
    (11, _("November")),
    (12, _("December")),
)

MONTH_SHORT = (
    (1, _("Jan")),
    (2, _("Feb")),
    (3, _("Mar")),
    (4, _("Apr")),
    (5, _("May")),
    (6, _("Jun")),
    (7, _("Jul")),
    (8, _("Aug")),
    (9, _("Sep")),
    (10, _("Oct")),
    (11, _("Nov")),
    (12, _("Dec")),
)


ORDINAL = (
    (1, _("first")),
    (2, _("second")),
    (3, _("third")),
    (4, _("fourth")),
    (-1, _("last")),
)

DURATION = (
    (30, _("30 min")),
    (60, _("1 hour")),
    (90, _("1.5 hours")),
    (120, _("2 hours")),
)


REPEAT_CHOICES = (
    ("count", _("By count")),
    ("until", _("Until date")),
)


ON_EACH = (("on", _("On the")), 
           ("each", _("Each:")))
