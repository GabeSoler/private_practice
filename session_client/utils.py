import pendulum as p


def time_plus_duration(time_obj, duration_obj):
    # Create a reference datetime with the time
    reference = p.now().at(time_obj.hour, time_obj.minute, time_obj.second)

    # Add the duration
    result = reference.add(seconds=duration_obj.total_seconds())

    # Return just the time
    return result.time()

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

