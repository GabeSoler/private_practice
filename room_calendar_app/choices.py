from datetime import datetime, date, time, timedelta
from django.utils.translation import gettext_lazy as _
import pendulum as p

def time_slot_options():
    """Creats a list tuples of time options from 8 to 22 every 15 min"""

    format = "%I:%M %p"
    options = []
    today = p.now()
    interval = p.interval(today.at(8),today.at(22))
    for dt in interval.range('minutes',30):
        options.append((str(dt.time()), dt.strftime(format)))
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


def duration_times_as_choices()->list:
    """ creates a list of tuples of duration"""
    choices_list = []
    for t in duration_times():
        choices_list.append((t,t))
    return choices_list
        


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
