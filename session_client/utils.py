import pendulum as p


def time_plus_duration(time_obj, duration_obj):
    seconds_in_day = 24 * 60 * 60
    total_seconds = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second +
                     int(duration_obj.total_seconds())) % seconds_in_day
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return p.time(hours, minutes, seconds)

def date_plus_time(date_obj, time_obj):
    return p.datetime(
        year=date_obj.year,
        month=date_obj.month,
        day=date_obj.day,
        hour=time_obj.hour,
        minute=time_obj.minute,
        second=time_obj.second
    )

def range_from_date(date_start, date_end, step=1, add_week_start=False,range_type='weeks'):
    datetime_start = p.now().on(date_start.year,date_start.month,date_start.day).start_of('day')
    if add_week_start:
        datetime_start = datetime_start.add(weeks=1)
    datetime_end = p.now().on(date_end.year,date_end.month,date_end.day).end_of('day')
    return p.interval(datetime_start, datetime_end).range(range_type, step)

