from django.shortcuts import render
from icalendar import Calendar, Event
import datetime


def display(cal):
    return cal.to_ical()#.replace('\r\n', '\n').strip()


def create_event(**kwargs):
    event = Event()
    for (key, value) in kwargs.items():
        event.add(key, value)
    return event


def date(dateobject):
    return datetime.datetime(dateobject.year,
                             dateobject.month,
                             dateobject.day,
                             dateobject.hour,
                             dateobject.minute,
                             dateobject.second).isoformat().replace(':','').replace('-','')


def enddate(dateobject):
    return datetime.datetime(dateobject.year,
                             dateobject.month,
                             dateobject.day,
                             dateobject.hour,
                             dateobject.minute,
                             dateobject.second).isoformat().replace(':','').replace('-','')


def events(events):
    cal = Calendar()
    #cal.add('prodid', '-//FC Tuhlaajapojat//What is this field//')
    cal.add('X-WR-CALNAME', 'FC Tuhlaajapojat')
    cal.add('version', '2.0')

    for event in events:
        cal.add_component(event)
    
    return display(cal)



