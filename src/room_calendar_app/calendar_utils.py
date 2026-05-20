""" A series of functions to deal with the calendar"""
import pendulum as p

from room_calendar_app.models import RoomCalendarModel
from base.choices import time_slots, WEEKDAY_SHORT
from session_client.utils import time_plus_duration, now_at_time
from base.choices import MONTH_LONG


def week_slot_dic() -> dict:
    week_dict = {}
    for slot in time_slots():
        week_dict[slot] = {}
        for i in range(1, 8):
            weekday = {i: set()}
            week_dict[slot].update(weekday)
    return week_dict


def day_slot_dic() -> dict:
    day_dict = {}
    for slot in time_slots():
        day_dict[slot] = {}
    return day_dict


class CalendarRender:
    """ A class to create calendar dictionaries and render in template
    date_ref default is now
   week_days, gives you the weekdays in a list,
   week_dict organises the sessions in a dictionary by time slot and day
    """

    def __init__(self, sessions, date_ref: p.DateTime = None, room_cal: RoomCalendarModel = None):
        self.sessions = sessions
        self.datetime = p.instance(date_ref) if date_ref else p.today()
        self.week_ref = self.datetime.week_of_year
        self.year_ref = self.datetime.year
        self.room_calendar = room_cal
        self.week_start = self.datetime.start_of('week')
        self.week_end = self.datetime.end_of('week')
        self.next_ref = self.datetime.add(weeks=1)
        self.prev_ref = self.datetime.subtract(weeks=1)

    @property
    def week_days(self) -> list:
        iter_week = p.interval(self.week_start, self.week_end)
        week_days_list = []
        for day in iter_week.range("days"):
            week_days_list.append(day)
        return week_days_list

    @property
    def week_dict(self) -> dict:
        """organises the dictionary by the session, it cannot handle two in a slot (which is the idea)"""
        week_dict = week_slot_dic()
        if not self.sessions:
            return week_dict
        for session in self.sessions:
            start_datetime = p.instance(session.start_datetime)  # annotated datetime
            end_datetime = p.instance(session.end_datetime_adjusted)  # adjusted with subtract min=30
            time_range = p.interval(start_datetime, end_datetime)
            iso_day = session.date.isoweekday()
            for time_slot in time_range.range('minutes', 30):
                slot = time_slot.time()
                week_dict[slot][iso_day] = session
        return week_dict


class CalendarBlocksRender:
    def __init__(self, blocks, room_cal: RoomCalendarModel = None):
        self.blocks = blocks
        self.week_days = WEEKDAY_SHORT
        self.room_calendar = room_cal

    @property
    def block_dict(self) -> dict:
        """organises the dictionary by the time blocks of tenants"""
        block_dict = week_slot_dic()
        if not self.blocks:
            return block_dict
        for block in self.blocks:
            # assert block.start_time is not None, "Calendar UtilsL: start_datetime should not be None"
            start_datetime = p.now().at(block.start_time.hour, block.start_time.minute)  # now() is ok!
            end_datetime = p.now().at(block.end_time.hour, block.end_time.minute).subtract(minutes=30)
            time_range = p.interval(start_datetime, end_datetime)
            iso_day = block.day + 1
            for time_slot in time_range.range('minutes', 30):
                slot = time_slot.time()
                block_dict[slot][iso_day] = block
        return block_dict


class CalendarTimesRender:
    def __init__(self, times, room_cal: RoomCalendarModel = None):
        self.times = times
        self.week_days = WEEKDAY_SHORT
        self.room_calendar = room_cal

    @property
    def times_dict(self) -> dict:
        """organises the dictionary by times default times in a week"""
        times_dict = week_slot_dic()
        if not self.times:
            return times_dict
        for time in self.times:
            # assert session.start_time is not None, "Calendar UtilsL: start_datetime should not be None"
            end_datetime = now_at_time(time.end_time).subtract(minutes=30)
            start_datetime = now_at_time(time.time)  # using now() is ok!
            time_range = p.interval(start_datetime, end_datetime)
            iso_day = time.day + 1
            for time_slot in time_range.range('minutes', 30):
                slot = time_slot.time()
                times_dict[slot][iso_day].add(time)
        return times_dict


class MonthNextUtil:
    def __init__(self, date_ref=p.now(), room_cal=None):
        self.date_ref = date_ref.start_of("month")
        self.room_calendar = room_cal
        self.next_ref = self.date_ref.add(months=1)
        self.prev_ref = self.date_ref.subtract(months=1)
        self.month = self.date_ref.format("YY-MM")
