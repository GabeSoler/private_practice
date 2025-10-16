""" A series of functions to deal with the calendar"""
from asyncio import TaskGroup
import time
import pendulum as p

from room_calendar_app.models import RoomCalendarModel
from session_client.choices import time_slots
from session_client.utils import date_plus_time

class CalendarRender:
    """ A class to create calendar dictionaries and render in template
    date_ref default is now
   week_days, gives you the weekdays in a list,
   week_dict organises the sessions in a dictionary by time slot and day
    """
    def __init__(self,sessions,date_ref:p.DateTime=None,room_cal=None):
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
    def week_slot_dic(self)->dict:
        week_dict = {}
        for slot in time_slots():
            week_dict[slot] = {}
            for i in range(1,8):
                weekday = {i:"empty"}
                week_dict[slot].update(weekday)
        return week_dict

    @property
    def day_slot_dic(self)->dict:
        day_dict = {}
        for slot in time_slots():
            day_dict[slot] = {}
        return day_dict

    @property
    def week_dict(self)->dict:
        """organises the dictionary by the session, it cannot handle two in a slot (which is the idea)"""
        week_dict = self.week_slot_dic
        time_1 = time.perf_counter()
        for session in self.sessions:
            #assert session.start_time is not None, "Calendar UtilsL: start_datetime should not be None"
            start_time = session.start_time
            end_time = p.time(session.end_time.hour,session.end_time.minute).subtract(minutes=30)
            start_datetime = date_plus_time(session.date,start_time) # session date! not self.datetime!
            end_datetime = date_plus_time(session.date,end_time)
            time_range = p.interval(start_datetime,end_datetime)
            iso_day = session.date.isoweekday()
            for time_slot in time_range.range('minutes',30):
                slot = time_slot.time()
                week_dict[slot][iso_day] = session
        time_2 = time.perf_counter()
        print("time week allocation", time_2-time_1)
        return week_dict
