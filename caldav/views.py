from django.shortcuts import render
from icalendar import Calendar, Event
import datetime

# Create your views here.


def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()


def create_event(**kwargs):
    event = Event()
    for (key, value) in kwargs.items():
        event[key] = value
    return event


def events(events):
    cal = Calendar()

    ## event = Event()
    ## event['uid'] = '42'
    ## event['summary'] = 'FMHM [in]: AC Huhhahuli'
    ## event['dtstart'] = '20150115T080000'
    ## event['location'] = 'Hakaniemi'
    ## event.add('attendee', 'Jaakko Luttinen')
    ## event.add('attendee', 'Markus Valkama')

    for event in events:
        cal.add_component(event)
    
    return display(cal)
