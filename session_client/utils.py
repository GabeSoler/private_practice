from datetime import datetime

import pendulum as p


def time_plus_duration(time_obj, duration_obj)->p.Time:
    seconds_in_day = 24 * 60 * 60
    total_seconds = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second +
                     int(duration_obj.total_seconds())) % seconds_in_day
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return p.time(hours, minutes, seconds)

def date_plus_time(date_obj, time_obj)->p.DateTime:
    return p.datetime(
        year=date_obj.year,
        month=date_obj.month,
        day=date_obj.day,
        hour=time_obj.hour,
        minute=time_obj.minute,
        second=time_obj.second
    )

def range_from_date(date_start, date_end, step=1, add_weeks=None,range_type='weeks'):
    datetime_start = p.datetime(date_start.year,date_start.month,date_start.day).start_of('day')
    if add_weeks:
        datetime_start = datetime_start.add(weeks=add_weeks)
    datetime_end = p.datetime(date_end.year,date_end.month,date_end.day).end_of('day')
    return p.interval(datetime_start, datetime_end).range(range_type, step)

def now_at_time(time)->p.DateTime:
    return p.now().at(time.hour,time.minute)