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


