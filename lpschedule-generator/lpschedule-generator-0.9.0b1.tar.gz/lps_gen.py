# -*- coding: utf-8 -*-
#
#   SPDX-License-Identifier: CC0-1.0
#
#   This file is part of lpschedule-generator.
#


import json
import re
import sys

import pytz

from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime
from os import path

from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vCalAddress, vText, vDatetime
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from mistune import Renderer, Markdown
from pytz import timezone
from unidecode import unidecode

from lpschedule_generator._version import __version__


# Python dictionary that will contain the lp schedule.
lps_dict = OrderedDict()

# Python dictionary that will contain the lp speakers.
lpspeakers_dict = OrderedDict()


def read_file(filename):
    """Read file and return it as a string.

    :param str filename: Absolute pathname of the file.

    """
    content = ''

    try:
        with open(filename, 'r') as f:
            for line in f:
                content = content + line
    except IOError:
        print('Error: unable to open {}'.format(filename))

    return content


def write_file(filename, filecontent):
    """Write `filecontent` to `filename`.

    :param str filename:
        Absolute pathname of the file.
    :param str filecontent:
        Data to write to `filename`.

    """
    file_ = None
    try:
      file_   = open(filename, 'w')
      file_.write(filecontent)
      file_.close()
    except IOError:
        print('Error creating and writing content to {}'.format(filename))
        exit(1)


def json_write(filename, obj):
    """Serialize `obj` to JSON formatted `str` to `filename`.

    `filename` is written relative to the current working directory.

    """
    write_file(filename, json.dumps(obj, ensure_ascii=False, indent=4))


def json_read(filename):
    """Deserialize JSON from `filename` into Python object.

    """
    if not path.isfile(filename):
        return False

    return json.loads(read_file(filename),
                      object_pairs_hook=OrderedDict)


class LPiCal(object):
    """Used for producing iCal for LP schedule.
    """

    def __init__(self, lps_dict, lp_year):
        self.lps_dict = lps_dict
        self.lp_year = str(lp_year)

        # Matches strings like '09:45 - 10:30: Lorem ipsum dolor sit.'
        self.timeslot_re = re.compile(r'(\d+:\d+).+?(\d+:\d+)'
                                      r'\s*[:-]?\s*(.+\b)?')
        # Matches strings like 'Saturday, March 19'
        self.month_day_re = re.compile(r'\w+,\s*([a-zA-Z]+)\s*(\d+)')

        self.cal = Calendar()
        self.cal.add('prodid', '-//lpschedule generator//mxm.dk//')
        self.cal.add('version', '2.0')
        self.cal.add('x-wr-calname', 'LibrePlanet {}'.format(self.lp_year))

        # RFC 2445 requires DTSTAMP to be in UTC. DTSTAMP is used in
        # VEVENT (Event object, see `add_event` method).
        self.dtstamp = vDatetime(datetime.now(pytz.utc))

        # used to generate uid for ical.
        self.ucounter = 0


    def gen_uid(self):
        """Returns an unique id.

        Used for Event object.
        """
        self.ucounter = self.ucounter + 1
        return '{}@LP{}@libreplanet.org'.format(str(self.ucounter),
                                                self.lp_year)


    def get_timeslot(self, s):
        """Get start and end time for a timeslot.
        """

        timeslot = self.timeslot_re.search(s)

        if not timeslot:
            return None, None, None

        t_start = timeslot.group(1)
        t_end = timeslot.group(2)
        name = timeslot.group(3) or ''

        return t_start, t_end, name


    def get_month_day(self, s):
        """Get month and day.
        """

        month_day = self.month_day_re.search(s)

        if (not month_day) or (len(month_day.groups()) < 2):
            return None, None

        month = month_day.group(1)
        day = month_day.group(2)

        return month, day


    def mk_datetime(self, month, day, time):
        """Returns datetime object (EST).
        """
        # Day %d
        # Month %B
        # Year %Y
        # Hour %H (24-hr)
        # Minute %M (zero padded)
        # Second %S (zero padded)
        datetime_fmt = '%d %B %Y %H:%M:%S'
        eastern = timezone('US/Eastern')

        hour = time.split(':')[0]
        minute = time.split(':')[1]
        datetime_str = '{} {} {} {}:{}:{}'.format(day, month,
                                                  self.lp_year,
                                                  hour.zfill(2),
                                                  minute.zfill(2),
                                                  '00')

        dt_object = datetime.strptime(datetime_str, datetime_fmt)

        return vDatetime(eastern.localize(dt_object))


    def mk_attendee(self, speaker):
        """Make Attendee to be added to an Event object.

        See `add_event` method.
        """
        # Get rid of HTML (<a> element, etc) in `speaker`
        speaker = BeautifulSoup(speaker, 'html.parser').get_text()

        attendee = vCalAddress('invalid:nomail')
        attendee.params['cn'] = vText(speaker)
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
        attendee.params['CUTYPE'] = vText('INDIVIDUAL')

        return attendee


    def add_event(self, month, day, t_start, t_end, t_name, session,
                      session_info):
        """Adds event to calendar.
        """
        event = Event()
        event['uid'] = self.gen_uid()
        event['dtstamp'] = self.dtstamp
        event['class'] = vText('PUBLIC')
        event['status'] = vText('CONFIRMED')
        event['method'] = vText('PUBLISH')

        if session == 'st-from-ts':
            event['summary'] = t_name
        else:
            event['summary'] = session

        event['location'] = vText(session_info['room'])

        # Get rid of HTML in 'desc'
        desc = BeautifulSoup(' '.join(
            session_info['desc']).replace(
                '\n', ' '), 'html.parser').get_text()
        event['description'] = desc

        # Add speakers
        for speaker in session_info['speakers']:
            event.add('attendee', self.mk_attendee(speaker), encode=0)

        dt_start = self.mk_datetime(month, day, t_start)
        dt_end = self.mk_datetime(month, day, t_end)

        event['dtstart'] = dt_start
        event['dtend'] = dt_end

        # Add to calendar
        self.cal.add_component(event)

        return event


    def gen_ical(self):
        """Parse LP schedule dict and generate iCal Calendar object.
        """

        for day_str, timeslots in self.lps_dict.items():
            month, day = self.get_month_day(day_str)
            if not month:
                # month, day not specified; cannot generate ical for
                # this day
                continue
            for timeslot_str, sessions in timeslots.items():
                t_start, t_end, t_name = self.get_timeslot(timeslot_str)
                if not t_start:
                    # timeslot not specified; cannot generate ical for
                    # this timeslot
                    continue
                for session, session_info in sessions.items():
                    self.add_event(month, day, t_start, t_end, t_name,
                                   session, session_info)

        return str(self.cal.to_ical())


    def to_ical(self):
        """Writes iCal to disk.
        """
        filename = 'lp{}-schedule.ics'.format(self.lp_year)
        write_file(filename, self.gen_ical())

        return filename


class LPSRenderer(Renderer):
    """Helps convert Markdown version of LP schedule to a dictionary.
    """

    def __init__(self, **kwargs):
        super(LPSRenderer, self).__init__(**kwargs)
        self.last_day = None
        self.last_time_slot = None
        self.last_session = None

        # Denotes the no. of the paragraph under a session; this
        # information will be helpful in identifying the "speaker",
        # "room" and session "description".
        self.no_paragraph = None

        # Contains a list of speakers' names which are marked up for
        # auto-linking[1], but don't have an id to link to.
        #
        # [1]: Markup for auto-linking speakers is [John Hacker]().
        self.speakers_noids = []

        # If it is 'False', then the 'speaker.ids' file was not found;
        # otherwise it is an OrderedDict containing the mapping of
        # speakers and their corresponding id.
        self.speakers_ids = json_read('speakers.ids')


    def get_uid(self, speaker):
        """Generate unique id for `speaker`.

        Returns unique id for `speaker` if it exists; `False` otherwise.
        """
        if not self.speakers_ids:
            # There is no speakers_ids OrderedDict available.
            return False

        speaker = str(speaker)
        if speaker in self.speakers_ids.keys():
            return self.speakers_ids[speaker]
        else:
            # speaker not found in speakers_ids OrderedDict.
            return False


    def _check_session_title_exists(self):
        """Checks if :py:attr:`.last_session` is set.

        If :py:attr:`.last_session` is not set and first paragraph is
        encountered, then it is assumed that the current timeslot is in
        the following format::

            ### 9:00 - 10:45: Opening Keynote - Beyond unfree...

            [Cory Doctorow][doctorow]

            Room 32-123

            Software has eaten the world...

        This method is meant to be called from the
        :py:method:`.paragraph` method.
        """
        if not self.last_session and self.no_paragraph == 0:
            # Current timeslot has only one session and there
            # no session title.
            #
            # st-from-ts -> session title from time slot.
            lps_dict[self.last_day][self.last_time_slot][
                'st-from-ts'] = OrderedDict()
            self.last_session = 'st-from-ts'


    def _process_video(self, text):
        """Process the video text.

        If it's a link, just extract the link and return it.

        This method is meant to be called from the
        :py:method:`.paragraph` method.
        """
        soup = BeautifulSoup(text, 'html.parser')
        links = soup.find_all('a')

        if len(links) == 0:
            # no links found, so
            return text

        # link(s) found, return the first link's href.
        return links[0]['href']

    def link(self, link, title, text):
        # Here, we catch speaker names that have to be autolinked and
        # autolink them if there is an id available for the speaker.
        if not link:
            # We found a speaker that has to be autolinked.

            # Here, `text` is the speaker' name.
            id_ = self.get_uid(text)
            if id_:
                link = 'speakers.html#{}'.format(id_)
            else:
                # Oh no, there is no id for this speaker.
                self.speakers_noids.append(text)
                # Don't linkify this speaker; they don't have an id.
                return text

        return super(LPSRenderer, self).link(link, title, text)


    def header(self, text, level, raw=None):
        global lps_dict

        if level == 2:
            # Add new day.
            lps_dict[text] = OrderedDict()
            self.last_day = text
        elif level == 3:
            # Add new timeslot
            lps_dict[self.last_day][text] = OrderedDict()
            self.last_time_slot = text
            # New timeslot, reset paragraphs processed and
            # last session.
            self.no_paragraph = 0
            self.last_session = None
        elif level == 4:
            # Add new session
            lps_dict[self.last_day][self.last_time_slot][
                text] = OrderedDict()
            self.last_session = text
            # We found a new session; set no of paragraphs processed
            # to 0.
            self.no_paragraph = 0

        return super(LPSRenderer, self).header(text, level, raw)


    def paragraph(self, text):
        global lps_dict

        self._check_session_title_exists()
        p = super(LPSRenderer, self).paragraph(text)

        if self.no_paragraph == 0:
            # Speaker
            speakers = text.split(', ')

            lps_dict[self.last_day][self.last_time_slot][
                self.last_session]['speakers'] = speakers
            self.no_paragraph = self.no_paragraph + 1
        elif self.no_paragraph == 1:
            # Room
            lps_dict[self.last_day][self.last_time_slot][
                self.last_session]['room'] = text
            self.no_paragraph = self.no_paragraph + 1
        elif self.no_paragraph == 2:
            lps_dict[self.last_day][self.last_time_slot][
                self.last_session]['video'] = self._process_video(text)
            # Initialize description
            lps_dict[self.last_day][self.last_time_slot][
                self.last_session]['desc'] = []
            self.no_paragraph = self.no_paragraph + 1
        elif self.no_paragraph > 1:
            lps_dict[self.last_day][self.last_time_slot][
                self.last_session]['desc'].append(text)

        return p


class LPSpeakersRenderer(Renderer):
    """Helps convert Markdown version of LP speakers to a dictionary.
    """

    def __init__(self, **kwargs):
        super(LPSpeakersRenderer, self).__init__(**kwargs)
        global lpspeakers_dict

        lpspeakers_dict = OrderedDict()
        lpspeakers_dict['keynote-speakers'] = []
        lpspeakers_dict['speakers'] = []

        # Type of present speaker being processed; can either be
        # 'keynote-speakers' or 'speakers'.
        self.speaker_type = None

        # Maintain a dict of speakers and their IDs.
        self.speakers_ids = OrderedDict()


    def mk_uid(self, speaker_block):
        """Returns a unique id.
        """
        # 'John HÖcker, Onion Project' -> 'John HÖcker'
        speaker = str(speaker_block.split(', ')[0])

        # 'John HÖcker' -> 'John Hacker'
        ascii_speaker = unidecode(speaker)

        # 'John Hacker' -> 'hacker'
        id_ = ascii_speaker.split()[-1].lower()

        if id_ not in self.speakers_ids.values():
            self.speakers_ids[speaker]= id_
            return id_
        else:
            # 'John Hacker' -> 'john_hacker'
            id_ = '_'.join([s.lower() for s in ascii_speaker.split()])
            self.speakers_ids[speaker] = id_
            return id_


    def header(self, text, level, raw=None):
        global lpspeakers_dict

        if level == 1:
            self.speaker_type = 'keynote-speakers'
            lpspeakers_dict[self.speaker_type].append(OrderedDict())

            lpspeakers_dict[self.speaker_type][-1]['speaker'] = text
            lpspeakers_dict[self.speaker_type][-1][
                'id'] = self.mk_uid(text)
            lpspeakers_dict[self.speaker_type][-1][
                'bio']  = []
        elif level == 2:
            self.speaker_type = 'speakers'
            lpspeakers_dict[self.speaker_type].append(OrderedDict())

            lpspeakers_dict[self.speaker_type][
                -1]['speaker'] = text.split(', ')[0]
            lpspeakers_dict[self.speaker_type][
                -1]['id'] = self.mk_uid(text)
            lpspeakers_dict[self.speaker_type][
                -1]['bio']  = []

        return super(LPSpeakersRenderer, self).header(text, level, raw)


    def image(self, src, title, text):
        global lpspeakers_dict

        lpspeakers_dict[self.speaker_type][-1]['img_url'] = src
        lpspeakers_dict[self.speaker_type][-1]['img_alt'] = text

        return super(LPSpeakersRenderer, self).image(src, title, text)


    def paragraph(self, text):
        global lpspeakers_dict

        p = super(LPSpeakersRenderer, self).paragraph(text)

        if text.startswith('<img'):
            # ignore
            return p

        lpspeakers_dict[self.speaker_type][-1]['bio'].append(text)
        return p


class LPSMarkdown(Markdown):
    """Converts MD LP schedule to a dictionary.

    Returns the Markdown version of LP schedule as a dictionary.
    """
    def __init__(self, inline=None, block=None, **kwargs):
        """
        Initialize with LPSRenderer as the renderer.
        """
        self.sessions_renderer = LPSRenderer()
        super(LPSMarkdown, self).__init__(
            renderer=self.sessions_renderer,
            inline=None, block=None,
            **kwargs)


    def parse(self, text):
        global lps_dict

        lps_dict = OrderedDict()
        html = super(LPSMarkdown, self).parse(text)

        # Write list of speakers with no ids to `speakers.noids`.
        json_write('speakers.noids',
                    self.sessions_renderer.speakers_noids)

        return lps_dict


class LPSpeakersMarkdown(Markdown):
    """Converts MD LP speakers to a dictionary.

    Returns the Markdown version of LP speakers as a dictionary.
    """

    def __init__(self, inline=None, block=None, **kwargs):
        """
        Initialize with LPSpeakersRenderer as the renderer.
        """
        self.speakers_renderer = LPSpeakersRenderer()
        super(LPSpeakersMarkdown, self).__init__(
            renderer=self.speakers_renderer,
            inline=None, block=None,
            **kwargs)


    def parse(self, text):
        global lpspeakers_dict

        html = super(LPSpeakersMarkdown, self).parse(text)

        # Write mapping of speakers and their ids to `speakers.ids`.
        json_write('speakers.ids', self.speakers_renderer.speakers_ids)

        return lpspeakers_dict


def RenderHTML(lp_dict, template):
    """Renders LP schedule/speakers in HTML from a python dictionary.

    Returns the HTML as a string.
    """
    env = Environment(loader=FileSystemLoader(path.dirname(template)),
                      trim_blocks=True, lstrip_blocks=True)

    template_name = path.basename(template)
    template  = None

    try:
        template = env.get_template(template_name)
    except TemplateNotFound as e:
        print('Template {} not found.'.format(template_name))
        exit(1)

    lp_html = template.render(lp_dict=lp_dict)

    return str(BeautifulSoup(lp_html, 'html.parser')).strip()


def main():
    parser = ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--schedule", action="store_true",
                       help="Generate LP schedule")
    group.add_argument("-sp", "--speakers", action="store_true",
                       help="Generate LP speakers")

    parser.add_argument("--ical", type=int,
                        help="Specify LP year as argument; "
                            + "generates iCal")
    parser.add_argument("--version", action="version",
                        version='lpschedule-generator version {}'
                        .format(__version__),
                        help="Show version number and exit.")
    parser.add_argument("lp_t",
                        help="Path to the LP template.")
    parser.add_argument("lp_md",
                        help="Path to the LP markdown.")
    args = parser.parse_args()

    lp_template = args.lp_t
    lp_md_content = read_file(path.abspath(args.lp_md))

    if path.exists(lp_template) and lp_md_content:

        if args.schedule:
            markdown = LPSMarkdown()
        elif args.speakers:
            markdown = LPSpeakersMarkdown()
        else:
            parser.error('No action requested, add -s or -sp switch')

        lp_dict = markdown(lp_md_content)
        lp_html = RenderHTML(lp_dict, lp_template)

        if args.ical and args.schedule:
            LPiCal(lp_dict, args.ical).to_ical()

    else:
        exit(1)

    if lp_html:
        # stdout lps html
        print(lp_html)
    else:
        print('Error generating LP HTML.')


if __name__ == "__main__":
    main()
