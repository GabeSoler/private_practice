""" A series of functions to deal with the calendar"""
import pendulum as p
from .choices import time_slots
from django.db.models import Q


class CalendarRender:
    """ A class to create calendar dictionaries and render in template """
    def __init__(self,occurrences,date=None):
        self.date = p.instance(date)
        self.occurrences = occurrences

    @property
    def week_days(self)->list:
        if self.date is None:
            date_ref = p.today()
        else:
            date_ref = self.date
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
        """organises the dictionary by the occurrence, it cannot handle two in a slot (which is the idea)"""
        week_dict = self.week_slot_dic
        for occurrence in self.occurrences:
            start_time = p.instance(occurrence.start_time)
            end_time = p.instance(occurrence.end_time).subtract(minutes=30)
            time_range = p.interval(start_time,end_time)
            iso_day = start_time.isoweekday()
            for time in time_range.range('minutes',30):
                slot = time.time()
                week_dict[slot][iso_day] = occurrence
        return week_dict

