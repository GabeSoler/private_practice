""" A series of functions to deal with the calendar"""
import pendulum as p
from choices import time_slots

def week_days(date=None)->list:
    if date != None:
        date_ref = p.today()
    else:
        date_ref = date
    week_start = date_ref.start_of("week")
    week_end = date_ref.end_of("week")
    iter_week = p.interval(week_start,week_end)
    week_days_list = []
    for day in iter_week.range("days"):
        week_days_list.append(day)
    return week_days_list

def slot_dic()->dict:
    week_dict = {}
    for slot in time_slots():
        week_dict[slot] = {}
        for i in range(1,8):
            weekday = {i:"empty"}
            week_dict[slot].update(weekday)
    return week_dict


def week_dict(occurrences:object):
    """organises the dictionary by the slots and allows multiple occurrences"""
    week_dict = slot_dic()
    week_days = week_days()
    for slot,day in week_dict.items():
        for d,_ in day.items():
            date = week_days[d-1]
            p_date = p.instance(date)
            iso_day = d
            dt_slot = p_date.at(hour=slot.hour,minute=slot.minute)
            input = occurrences.filter(
                Q(start_time=dt_slot) | Q(end_time__lte=dt_slot.subtract(minutes=30)), start_time__iso_week_day=iso_day)
                #todo make a Q that includes endtime. Maybe convert the slot into a datetime object to make finetuning easier? as I need to add
            week_dict[slot][iso_day] = input         
    return week_dict

def week_dict_occ(occurrences):
    """organises the dictionary by the occurrence"""
    week_dict = slot_dic()
    for occurrence in occurrences:
        start_time = p.instance(occurrence.start_time)
        end_time = p.instance(occurrence.end_time)
        time_range = p.interval(start_time,end_time)
        iso_day = start_time.isoweekday()
        for time in time_range.range('minutes',30):
            slot = time.time()
            week_dict[slot][iso_day] = occurrence
    return week_dict

