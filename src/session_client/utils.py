import csv
import datetime

import pendulum as p
from django.http import HttpResponse

from room_calendar_app.models import RoomCalendarModel


def time_plus_duration(time_obj: datetime.time, duration_obj) -> p.Time:
    seconds_in_day = 24 * 60 * 60
    if not isinstance(time_obj, datetime.time):
        time = p.parse(time_obj)
    else:
        time = time_obj
    total_seconds = (time.hour * 3600 + time.minute * 60 + time.second +
                     int(duration_obj.total_seconds())) % seconds_in_day
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return p.time(hours, minutes, seconds)


def date_plus_time(date_obj, time_obj) -> p.DateTime:
    return p.datetime(
        year=date_obj.year,
        month=date_obj.month,
        day=date_obj.day,
        hour=time_obj.hour,
        minute=time_obj.minute,
        second=time_obj.second
    )


def range_from_date(date_start, date_end, step=1, add_weeks=None, range_type='weeks'):
    datetime_start = p.datetime(date_start.year, date_start.month, date_start.day).start_of('day')
    if add_weeks:
        datetime_start = datetime_start.add(weeks=add_weeks)
    datetime_end = p.datetime(date_end.year, date_end.month, date_end.day).end_of('day')
    return p.interval(datetime_start, datetime_end).range(range_type, step)


def now_at_time(time) -> p.DateTime:
    return p.now().at(time.hour, time.minute)


def make_csv_response(file_name):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{file_name}.csv"'})
    return response


def csv_session_list_response(sessions, client, date_start, date_end):
    start_ref_str = p.instance(date_start).to_formatted_date_string()  # converting for easier formatting
    end_ref_str = p.instance(date_end).to_formatted_date_string()
    file_name = f"{client}: {start_ref_str}-{end_ref_str}" if client else f"{start_ref_str}-{end_ref_str}"
    response = make_csv_response(file_name)
    fieldnames = ["date", "start_time", "client" "paid"]
    writer = csv.writer(response)  # response is the output
    writer.writerow(fieldnames)
    for row in sessions:
        writer.writerow([row.date, row.start_time, row.client, row.keywords, row.paid])
    return response


def csv_room_report_response(sessions, room: RoomCalendarModel, year: int, month: int):
    file_name = f"{room}: {year}-{month}"
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{file_name}.csv"'})
    fieldnames = ["id", "date", "type", "agreement", "pay"]
    writer = csv.writer(response)  # response is the output
    writer.writerow(fieldnames)
    for row in sessions:
        writer.writerow([row.uuid, row.date, row.client.type, row.tenant.display_name, row.pay])
    return response
