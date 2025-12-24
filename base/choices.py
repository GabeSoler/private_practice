from datetime import time, timedelta
from django.utils.translation import gettext_lazy as _
import pendulum as p
from typing import Tuple,Any,List

AGREEMENT_CHOICES = (
("Amount",_("By Amount")),
("Percentage",_("By Percentage")),
("Block",_("By Block")),
)

ATTENDANCE = [
    ("Attended", _("Attended")),
    ("LateC", _("Late Cancel")),
    ("Missed", _("Missed")),
    ("Cancel", _("Cancelled")),
]

CLIENT_TYPE = [
    ("Private", _("Private")),
    ("RoomP", _("Room Percentage")),
    ("Agency", _("Agency")),
    ("EAP", _("EAP")),
    ("SuperV", _("Supervisee")),
    ("Other", _("Other")),
]


SERIES_CHOICE = [
    (1, _("Every week")),
    (2, _("Every two weeks")),
]


def time_slot_options()->List[Tuple[Any,Any]]:
    """Creates a list tuples of time options from 8 to 22 every 15 min"""
    date_format = "%I:%M %p"
    options = []
    today = p.now()
    interval = p.interval(today.at(8),today.at(22))
    for dt in interval.range('minutes',30):
        options.append((dt.time(),dt.strftime(date_format)))
    return options




def time_slots()->list:
    """ Creates a list with time slots from 8 am to 10 pm every 15 minutes """
    slots = []
    for x in range(80,220,5):# 80 == 8:00 am
        hour = x//10 #division without residual
        minute = x%10*6 #residual for steps ending in 5 times 6 == 30
        slot = time(hour=hour,minute=minute) #creates multiple choices for a time select
        slots.append(slot)
    return slots




def duration_times()->tuple[timedelta,timedelta,timedelta,timedelta,timedelta]:
    """ Creates a list of durations """
    return (
            timedelta(minutes=30),
            timedelta(hours=1),
            timedelta(minutes=90),
            timedelta(hours=2),
            timedelta(hours=3),
            )


def duration_times_as_choices()->list:
    """ creates a list of tuples of duration"""
    choices_list = []
    for t in duration_times():
        choices_list.append((t,str(t)))
    return choices_list
        


EVENT_TYPE = [
    ("client", _("Client's Session")),
    ("super", _("Supervision")),
    ("Admin", _("Admin")),
    ("Processing", _("Processing")),
    ("CPD", _("CPD")),
]


WEEKDAY_SHORT = (
    (0, _("Mon")),
    (1, _("Tue")),
    (2, _("Wed")),
    (3, _("Thu")),
    (4, _("Fri")),
    (5, _("Sat")),
    (6, _("Sun")),
)

WEEKDAY_LONG = (
    (0, _("Monday")),
    (1, _("Tuesday")),
    (2, _("Wednesday")),
    (3, _("Thursday")),
    (4, _("Friday")),
    (5, _("Saturday")),
    (6, _("Sunday")),
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

def years_choices(n=15):
    start_date = p.now()
    end_date = start_date.subtract(years=n)
    interval = p.interval(start_date,end_date)
    year_choices = [(y.year,f"{y.year}") for y in interval.range('years')]
    return year_choices

from collections import namedtuple
import pendulum as p
from django.utils.translation import gettext_lazy as _


PERIOD_TYPE_CHOICES = (
("quarter",_("quarter")),
("year",_("year")),
("tax_year",_("tax_year")),
)

QUARTER_CHOICES = (
("1",_("first quarter")),
("2",_("second quarter")),
("3",_("third quarter")),
("4",_("fourth quarter")),
)

QuarterRanges = namedtuple("QuarterRanges",["first","second","third","fourth"])
Date = namedtuple("Date",["day","month"])
Range = namedtuple("Range",["start","end"])
YearTypes = namedtuple("YearTypes",["jan_dec","apr_apr","apr_march","jul_jun","mar_mar"])

quarter_ranges = QuarterRanges(
    Range(Date(1,1),Date(31,3)),
    Range(Date(1,4),Date(30,5)),
    Range(Date(1,7),Date(30,9)),
    Range(Date(1,10),Date(31,12))
)

TAX_YEAR_TYPE_CHOICES = (
("jan-dec",_("January(1)-December(31)")),
("apr-apr",_("April(6)-April(5)")),
("apr-mar",_("April(1)-March(31)")),
("jul-jun",_("July(1)-June(30)")),
("mar-mar",_("March(21)-March(20)")),
)

year_types = YearTypes(
    Range(Date(1,1),Date(31,12)),
    Range(Date(6,4),Date(5,4)),
    Range(Date(1,4),Date(31,3)),
    Range(Date(1,6),Date(31,5)),
    Range(Date(21,3),Date(20,3)),
)

def create_year_range_dates(year_type,year):
    """ returns a date start and end date for a given year structure """
    year_range = getattr(year_types, year_type.replace("-", "_"))
    start_date = p.date(year,year_range.start.month,year_range.start.day)
    end_date = p.date(year,year_range.end.month,year_range.end.day)
    return start_date,end_date

def create_quarter_range_dates(quarter_n:int,year):
    """ returns a date start and end date for a given quarter in a given year """
    quarter_number = quarter_n - 1
    quarter_range = quarter_ranges[quarter_number]
    start_date = p.date(year,quarter_range.start.month,quarter_range.start.day)
    end_date = p.date(year,quarter_range.end.month,quarter_range.end.day)
    return start_date,end_date


