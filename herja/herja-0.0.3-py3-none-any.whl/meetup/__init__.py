import logging
import os
import random

from .. import sleep
from ..conversions import html_to_soup
from ..net import Session, get_form_inputs
from ..settings import Settings


# global constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETUP_SETTINGS_JSON = os.path.join(BASE_DIR, 'settings.json')
MEETUP_LOGIN_URL = 'https://secure.meetup.com/login/'
MEETUP_GROUP_URL = 'https://www.meetup.com/{0}/'
MEETUP_EVENTS_URL = 'https://www.meetup.com/{0}/events/'


# global class objects
session = Session()
settings = Settings(MEETUP_SETTINGS_JSON)
settings.read()


def authenticate():
    """
    Authenticate the global module session with the server.
    """
    global settings

    email = settings['email']
    password = settings['password']

    # if a value was set during this authentication, save our settings
    if settings.changed:
        settings.write()

    response = session.get(MEETUP_LOGIN_URL)
    assert response.ok, 'Meetup login url request failed: {0}'.format(response)
    soup = html_to_soup(response.content)

    login_form = soup.find('form', {'id': 'loginForm'})
    assert login_form is not None, 'Failed to find login form.'

    inputs = get_form_inputs(login_form)
    with Settings() as settings:
        inputs['username'] = email
        inputs['password'] = password

    sleep(8)  # look natural

    response = session.post(login_form.attrs['action'], params=inputs)
    logging.info(response)

    sleep(6)  # look natural

    return response.ok


def get_group_events(group):
    """
    Obtain the events of a particular group.
    """
    response = session.get(MEETUP_GROUP_URL.format(group))
    assert response.ok, 'Meetup group url request failed: {0}'.format(response)

    soup = html_to_soup(response.content)
    event_cards = soup.find_all('div', {'class': 'eventCard'})

    events = []
    for event_card in event_cards:

        event = {}

        title = event_card.find('a', {'class': 'eventCardHead--title'})
        event['title'] = title.text.strip()
        event['link'] = title.attrs['href']

        time_display = event_card.find('div', {'class': 'eventTimeDisplay'})
        event['date'] = time_display.text.strip()
        if event['date'] == 'Needs a date and time':
            event['date'] = None
        time_display_time = time_display.find('time')
        event['epoch'] = None if time_display_time is None else time_display_time.attrs['datetime']

        # this works on events with no set time
        venue_display = event_card.find('p', {'class': 'venueDisplay'})
        if venue_display is None:
            # works for events with a set time
            venue_display = event_card.find('div', {'class': 'venueDisplay'})

        # unable to obtain the venue
        if venue_display is None:
            event['venue'] = None
            print(event_card.prettify())
        else:
            event['venue'] = venue_display.text.strip()

        attendees = event_card.find('ul', {'class': 'eventCard--attendeesLink'})
        avatars = attendees.find_all('span', {'class': 'avatar'})
        event['attendees'] = [avatar.text.strip() for avatar in avatars]
        attending_count = event_card.find('li', {'class': 'avatarRow--attendingCount'})
        event['attendee_count'] = int(attending_count.text.strip().split(' ')[0])

        events.append(event)

    return events
