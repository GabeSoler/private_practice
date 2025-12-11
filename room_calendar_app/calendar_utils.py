""" A series of functions to deal with the calendar"""
from collections import namedtuple

import pendulum as p

from room_calendar_app.models import RoomCalendarModel, BlocksModel
from session_client.choices import time_slots,WEEKDAY_SHORT
from session_client.models import ClientModel
from session_client.utils import date_plus_time, time_plus_duration, now_at_time


def week_slot_dic() -> dict:
    week_dict = {}
    for slot in time_slots():
        week_dict[slot] = {}
        for i in range(1, 8):
            weekday = {i: "empty"}
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
    def __init__(self,sessions,date_ref:p.DateTime=None,room_cal:RoomCalendarModel=None):
        self.sessions = sessions
        self.datetime = p.instance(date_ref) if date_ref else p.today()
        self.week_ref = self.datetime.week_of_year
        self.year_ref = self.datetime.year
        self.room_calendar = room_cal

    @property
    def week_days(self)->list:
        date_ref = self.datetime
        week_start = date_ref.start_of("week")
        week_end = date_ref.end_of("week")
        iter_week = p.interval(week_start,week_end)
        week_days_list = []
        for day in iter_week.range("days"):
            week_days_list.append(day)
        return week_days_list

    @property
    def week_dict(self)->dict:
        """organises the dictionary by the session, it cannot handle two in a slot (which is the idea)"""
        week_dict = week_slot_dic()
        if not self.sessions:
            return week_dict
        for session in self.sessions:
            start_datetime = p.instance(session.start_datetime) #annotated datetime
            end_datetime = p.instance(session.end_datetime_adjusted) #adjusted with subtract min=30
            time_range = p.interval(start_datetime,end_datetime)
            iso_day = session.date.isoweekday()
            for time_slot in time_range.range('minutes',30):
                slot = time_slot.time()
                week_dict[slot][iso_day] = session
        return week_dict


class CalendarBlocksRender:
    def __init__(self,blocks:list[BlocksModel],calendar=None):
        self.blocks = blocks
        self.week_days = WEEKDAY_SHORT
        self.room_calendar = calendar

    @property
    def block_dict(self)->dict:
        """organises the dictionary by the time blocks of tenants"""
        block_dict = week_slot_dic()
        if not self.blocks:
            return block_dict
        for block in self.blocks:
            #assert block.start_time is not None, "Calendar UtilsL: start_datetime should not be None"
            start_datetime = p.now().at(block.start_time.hour,block.start_time.minute) # now() is ok!
            end_datetime = p.now().at(block.end_time.hour,block.end_time.minute).subtract(minutes=30)
            time_range = p.interval(start_datetime,end_datetime)
            iso_day = block.day
            for time_slot in time_range.range('minutes',30):
                slot = time_slot.time()
                block_dict[slot][iso_day] = block
        return block_dict

class CalendarClientsRender:
    def __init__(self,clients:list[ClientModel],calendar=None):
        self.clients = clients
        self.week_days = WEEKDAY_SHORT
        self.room_calendar = calendar

    @property
    def client_dict(self)->dict:
        """organises the dictionary by clients default times in a week"""
        client_dict = week_slot_dic()
        if not self.clients:
            return client_dict
        for client in self.clients:
            #assert session.start_time is not None, "Calendar UtilsL: start_datetime should not be None"
            end_time = time_plus_duration(client.time,client.duration)
            start_datetime = now_at_time(client.time) # using now() is ok!
            end_datetime = now_at_time(end_time).subtract(minutes=30)
            time_range = p.interval(start_datetime,end_datetime)
            iso_day = client.day +1
            for time_slot in time_range.range('minutes',30):
                slot = time_slot.time()
                client_dict[slot][iso_day] = client
        return client_dict