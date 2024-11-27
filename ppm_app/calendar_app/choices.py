from dateutil import rrule
from datetime import datetime, date, time, timedelta
from .conf import swingtime_settings
from . import utils


MINUTES_INTERVAL = swingtime_settings.TIMESLOT_INTERVAL.seconds // 60
SECONDS_INTERVAL = utils.time_delta_total_seconds(
    swingtime_settings.DEFAULT_OCCURRENCE_DURATION
)


def timeslot_options():
    """
Creats a list of time options from 8 to 21 every 15 min
    """

    interval = timedelta(minutes=15)
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




default_timeslot_options = timeslot_options()




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

FREQUENCY_CHOICES = (
    (rrule.DAILY, _("Day(s)")),
    (rrule.WEEKLY, _("Week(s)")),
    (rrule.MONTHLY, _("Month(s)")),
    (rrule.YEARLY, _("Year(s)")),
)

REPEAT_CHOICES = (
    ("count", _("By count")),
    ("until", _("Until date")),
)

ISO_WEEKDAYS_MAP = (
    None,
    rrule.MO,
    rrule.TU,
    rrule.WE,
    rrule.TH,
    rrule.FR,
    rrule.SA,
    rrule.SU,
)

ON_EACH = (("on", _("On the")), 
           ("each", _("Each:")))
