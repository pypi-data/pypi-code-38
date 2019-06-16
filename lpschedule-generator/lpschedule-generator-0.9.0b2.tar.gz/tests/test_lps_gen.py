# -*- coding: utf-8 -*-
#
#   SPDX-License-Identifier: CC0-1.0
#
#   This file is part of lpschedule-generator.
#


import json
import os

import mistune
import mock

from collections import OrderedDict
from os import path
from io import StringIO

from bs4 import BeautifulSoup
from icalendar import vCalAddress, vText, vDatetime
from nose.tools import *
from pytz import timezone

from lps_gen import *


class TestJSONUtils(object):
    """Class that tests json utils in `lps_gen` module.
    """
    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class."""
        self.speakers_ids = OrderedDict({
            'Daniel Kahn Gillmor': 'gillmor',
            'Edward Snowden': 'snowden',
            'Richard Stallman': 'stallman',
            'Clara Snowden': 'clara_snowden',
            'Ludovic Courtès': 'courtes',
            'Jonas Öberg': 'aberg',
        })
        self.ids_filename = 'speakers.ids'

        self.speakers_noids = [
            'Daniel Kahn Gillmor',
            'Richard Stallman',
            'Ludovic Courtès',
            'Jonas Öberg',
        ]
        self.noids_filename = 'speakers.noids'

        # Change current working directory to the tests directory.
        self.old_cwd = os.getcwd()
        os.chdir('tests')


    def setup(self):
        """Runs before each test in this class."""
        pass


    def test_json_write(self):
        """Testing json_write function."""
        json_write(self.ids_filename, self.speakers_ids)
        assert_equal(json.loads(read_file(self.ids_filename),
                                object_pairs_hook=OrderedDict),
                     self.speakers_ids)

        json_write(self.noids_filename, self.speakers_noids)
        assert_equal(json.loads(read_file(self.noids_filename),
                                object_pairs_hook=OrderedDict),
                     self.speakers_noids)


    def test_json_read(self):
        """Testing json_read function."""
        write_file(self.ids_filename, json.dumps(self.speakers_ids,
                                             indent=4))
        assert_equal(json_read(self.ids_filename), self.speakers_ids)

        write_file(self.noids_filename, json.dumps(self.speakers_noids,
                                             indent=4))
        assert_equal(json_read(self.noids_filename), self.speakers_noids)


    def teardown(self):
        """Cleans up things after each test in this class."""
        # Remove `speakers.ids` file if it exists.
        if path.isfile(self.ids_filename):
            os.remove(self.ids_filename)

        # Remove `speakers.noids` file if it exists.
        if path.isfile(self.noids_filename):
            os.remove(self.noids_filename)


    @classmethod
    def teardown_class(self):
        """Clean up the mess created by this test."""
        # Change back to the old cwd
        os.chdir(self.old_cwd)


class TestLPiCal(object):
    """
    Testing LPiCal class.
    """

    @classmethod
    def setup_class(self):
        """Setting up things for Testing LPiCal class.
        """

        # Change current working directory to the tests directory.
        self.old_cwd = os.getcwd()
        os.chdir('tests')

        self.MD_FILE = path.join('files', 'lp-sch.md')
        self.MD_FILE_CONTENT = read_file(self.MD_FILE)

        self.MD_FILE_S_ONLY = path.join('files', 'lp-sch-sessions-only.md')
        self.MD_FILE_S_ONLY_CONTENT = read_file(self.MD_FILE_S_ONLY)

        self.SCH_TEMPLATE = path.join('..', 'libreplanet-templates/2019',
                                      'lp-schedule.jinja2')

        self.markdown = LPSMarkdown()
        self.lps_dict = self.markdown(self.MD_FILE_CONTENT)
        self.lps_dict_s_only = self.markdown(self.MD_FILE_S_ONLY_CONTENT)
        self.purge_list = ['speakers.noids']


    def setup(self):
        """Setting up things for a new test.
        """
        self.lp_ical = LPiCal(self.lps_dict, '2019')


    def test_init(self):
        """Testing LPiCal.__init__.
        """
        lp_ical = LPiCal(self.lps_dict, '2019')

        assert_equal(lp_ical.lp_year, '2019')
        assert_equal(lp_ical.cal.get('x-wr-calname'),
                     'LibrePlanet 2019')
        assert_equal(lp_ical.ucounter, 0)


    def test_gen_uid(self):
        """Testing LPiCal.gen_uid.
        """

        uid_fmt = ''.join(['{id}@LP', self.lp_ical.lp_year,
                           '@libreplanet.org'])

        for i in range(40):
            assert_equals(self.lp_ical.gen_uid(),
                          uid_fmt.format(id=i+1))


    def test_get_timeslot(self):
        """
        Testing LPiCal.get_timeslot.
        """

        timeslots = {
            '09:00-09:45: Registration and Breakfast':
            ['09:00', '09:45', 'Registration and Breakfast'],
            '  09:45 - 10:45: Opening Keynote':
            ['09:45', '10:45', 'Opening Keynote'],
            '10:5 - 10:55: Break':
            ['10:5', '10:55', 'Break'],
            ' 10:55 - 11:40: Session Block 1A':
            ['10:55', '11:40', 'Session Block 1A'],
            '    11:40 - 11:50: Break':
            ['11:40', '11:50', 'Break'],
            '9:45 - 10:30: Keynote ':
            ['9:45', '10:30', 'Keynote'],
            '16:55 - 17:40:Session Block 6B':
            ['16:55', '17:40', 'Session Block 6B'],
            '17:50 - 18:35: Closing keynote':
            ['17:50', '18:35', 'Closing keynote'],
            '':
            [None, None, None],
            '\t\t\t':
            [None, None, None],
            '                  ':
            [None, None, None],
            '10:00 - 10:45 - Keynote':
            ['10:00', '10:45', 'Keynote'],
            '16:20 - 17:05':
            ['16:20', '17:05', ''],
            '16:25-17:25':
            ['16:25', '17:25', ''],
            '17:05-17:15 - Break':
            ['17:05', '17:15', 'Break']
        }

        for string, timeslot in timeslots.items():
            start, end, name = self.lp_ical.get_timeslot(string)
            assert_equal(start, timeslot[0])
            assert_equal(end, timeslot[1])
            assert_equal(name, timeslot[2])


    def test_get_month_day(self):
        """Testing LPiCal.get_month_day.
        """

        month_days = {
            'Sunday, March 20': ['March', '20'],
            'Saturday, March 19': ['March', '19'],
            'Monday,March 20 ': ['March', '20'],
            'Tuesday,March21': ['March', '21'],
            '   Wednesday, March 22': ['March', '22'],
            'Thursday, March 23  ': ['March', '23'],
            '': [None, None],
            '\t\t': [None, None],
            '       ': [None, None],
        }

        for string, month_day in month_days.items():
            month, day  = self.lp_ical.get_month_day(string)
            assert_equal(month, month_day[0])
            assert_equal(day, month_day[1])


    def test_mk_datetime(self):
        """Testing LPiCal.mk_datetime
        """

        datetimes = [
            {
                'params': ['February', '28','08:00'],
                'datetime': '2019-02-28 08:00:00',
            },
            {
                'params': ['March', '21', '9:0'],
                'datetime': '2019-03-21 09:00:00',
            },
            {
                'params': ['March', '23', '15:30'],
                'datetime': '2019-03-23 15:30:00',
            },
        ]

        for test in datetimes:
            month = test['params'][0]
            day = test['params'][1]
            time = test['params'][2]

            dt_obj = self.lp_ical.mk_datetime(month, day, time)

            assert str(dt_obj.dt.tzinfo) == 'US/Eastern'
            assert str(dt_obj.dt)[:-6] == test['datetime']


    def test_mk_attendee(self):
        """Testing LPiCal.mk_attendee
        """
        speakers = [
            'Richard Stallman',
            'ginger coons',
            '<a href="speakers.htmll#corvellec">Marianne Corvellec</a>',
            '<a href="speakers.html#le-lous">Jonathan Le Lous</a>',
            'Jonas \xc3\x96berg',
            ]

        for speaker in speakers:
            attendee = self.lp_ical.mk_attendee(speaker)
            assert str(attendee) == 'invalid:nomail'
            assert attendee.params.get('cn') == BeautifulSoup(
                speaker, 'html.parser').get_text()
            assert attendee.params.get('ROLE') == 'REQ-PARTICIPANT'
            assert attendee.params.get('CUTYPE') == 'INDIVIDUAL'


    def test_add_event(self):
        """Testing LPiCal.add_event
        """
        uids = []

        for day_str, timeslots in self.lps_dict.items():
            month, day = self.lp_ical.get_month_day(day_str)
            for timeslot_str, sessions in timeslots.items():
                t_start, t_end, t_name = self.lp_ical.get_timeslot(timeslot_str)
                for session, session_info in sessions.items():
                    event = self.lp_ical.add_event(month, day,
                                            t_start, t_end, t_name,
                                            session, session_info)
                    assert event['uid'] not in uids
                    uids.append(event['uid'])

                    assert event['dtstamp'] == self.lp_ical.dtstamp
                    assert event['class'] == 'PUBLIC'
                    assert event['status'] == 'CONFIRMED'
                    assert event['method'] == 'PUBLISH'

                    if session == 'st-from-ts':
                        assert event['summary'] == t_name
                    else:
                        assert event['summary'] == session

                    assert event['location'] == session_info['room']
                    assert event['description'] == BeautifulSoup(' '.join(
                        session_info['desc']).replace(
                            '\n',' '), 'html.parser').get_text()

                    if type(event['attendee']) is list:
                        for attendee in event['attendee']:
                            assert isinstance(attendee, vCalAddress)
                    else:
                        assert isinstance(event['attendee'], vCalAddress)

                    assert isinstance(event['dtstart'], vDatetime)
                    assert isinstance(event['dtend'], vDatetime)


    def test_gen_ical(self):
        """Testing LPiCal.gen_ical.
        """
        print(self.lp_ical.gen_ical())


    def test_gen_ical_sessions_only(self):
        """Testing LPiCal.gen_ical with sessions only schedule.
        """
        print(LPiCal(self.lps_dict_s_only, '2019').gen_ical())


    def test_to_ical(self):
        """Testing LPiCal.to_ical.
        """
        filename = self.lp_ical.to_ical()
        assert_equal(filename, 'lp2019-schedule.ics')

        self.purge_list.append(filename)


    @classmethod
    def teardown_class(self):
        """
        Tearing down the mess created by Testing LPiCal class.
        """

        # remove files in the purge_list.
        for f in self.purge_list:
            if path.isfile(f):
                os.remove(f)

        # Change back to the old cwd
        os.chdir(self.old_cwd)


class TestLPS(object):
    """
    Class that tests everything related LP Schedule.
    """
    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class."""

        # Change current working directory to the tests directory.
        self.old_cwd = os.getcwd()
        os.chdir('tests')

        self.MD_FILE = path.join('files', 'lp-sch.md')
        self.MD_FILE_CONTENT = read_file(self.MD_FILE)

        self.SCH_TEMPLATE = path.join('..', 'libreplanet-templates/2019',
                                      'lp-schedule.jinja2')

        self.markdown = LPSMarkdown()
        self.lps_dict = self.markdown(self.MD_FILE_CONTENT)

    def setup(self):
        """Runs before each test in this class."""
        pass


    def test_LPSMarkdown_day(self):
        """
        Testing `LPSMarkdown` class - Day.
        """
        days = ['Saturday, March 19',
                'Sunday, March 20']
        i = 0
        for day in self.lps_dict.keys():
            assert_equal(day, days[i])
            i = i + 1


    def test_LPSMarkdown_timeslot(self):
        """
        Testing `LPSMarkdown` class - Timeslot.
        """
        timeslots = [
            '09:00 - 09:45: Registration and Breakfast',
            '09:45 - 10:45: Opening Keynote: Richard Stallman',
            '10:55 - 11:40: Session Block 1A',
            '11:40 - 11:50: Break',
            '11:50 - 12:35: Session Block 2A',
            '09:00 - 09:45: Registration and breakfast',
            '09:45 - 10:30: Keynote: Access without empowerment',
            '10:30 - 10:40: Break',
            '10:40 - 11:25: Session Block 1B',
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for timeslot in lps_timeslots.keys():
                assert_equal(timeslot, timeslots[i])
                i = i + 1


    def test_LPSMarkdown_session(self):
        """
        Testing `LPSMarkdown` class - Session.
        """
        sessions = [
            'Free software, free hardware, and other things',
            'Federation and GNU',
            'Dr. Hyde and Mr. Jekyll: advocating for free software in nonfree academic contexts',
            'TAFTA, CETA, TISA: traps and threats to Free Software Everywhere',
            'Let\'s encrypt!',
            'Attribution revolution -- turning copyright upside-down',
            'st-from-ts',
            'Fork and ignore: fighting a GPL violation by coding instead',
            'Who did this? Just wait until your father gets home',
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session in lps_sessions.keys():
                    assert_equal(session, sessions[i])
                    i = i + 1


    def test_LPSMarkdown_speaker(self):
        """
        Testing `LPSMarkdown` class - Speaker
        """
        speakers = [
            ['Richard Stallman'],
            ['<a href="http://dustycloud.org">Christopher Webber</a>'],
            ['ginger coons'],
            ['<a href="/2015/program/speakers.html#corvellec">Marianne Corvellec</a>',
             '<a href="/2015/program/speakers.html#le-lous">Jonathan Le Lous</a>'],
            ['Seth Schoen'],
            ['Jonas Öberg'],
            ['Benjamin Mako Hill'],
            ['Bradley Kuhn'],
            ['Ken Starks'],
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['speakers'], speakers[i])
                    i = i + 1


    def test_LPSMarkdown_room(self):
        """
        Testing `LPSMarkdown` class - Room
        """
        rooms = [
            'Room 32-123',
            'Room 32-123',
            'Room 32-141',
            'Room 32-155',
            'Room 32-123',
            'Room 32-141',
            'Room 32-123',
            'Room 32-123',
            'Room 32-141',
            ]
        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['room'], rooms[i])
                    i = i + 1


    def test_LPSMarkdown_video(self):
        """Testing `LPSMarkdown` class - Video
        """

        videos = [
            'https://media.libre.planet/rms-free-everything',
            'https://media.libre.planet/gnu-fed',
            'VideoTBA',
            'https://media.libre.planet/tafta-ceta-tisa',
            'https://media.libre.planet/letsencrypt',
            'VideoTBA',
            'https://media.libre.planet/mako-keynote',
            'https://media.libre.planet/fork-ignore',
            'VideoTBA',
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['video'], videos[i])
                    i = i + 1


    def test_LPSMarkdown_desc(self):
        """Testing `LPSMarkdown` class - Video
        """
        descriptions = [
            'Preceded by a welcome address from',
            'The effort to re-decentralize the web has',
            'What if the classic horror trope of the',
            'TAFTA, CETA, and TISA are far-reaching',
            'This year a robotic certificate authority will',
            'Reusing works licensed under free licenses seems',
            'In order to relate effectively to the digital works',
            'The free software movement has twin',
            'Typically, GPL enforcement activity',
            'While traditional enforcement is often',
            'Recently, Software Freedom Conservancy',
            'This talk discusses which scenarios make this remedy',
            'What\'s going on in here? Computer parts',
        ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    for desc in session_info['desc']:
                        assert_true(desc.startswith(descriptions[i]))
                        i = i + 1


    def test_RenderHTML(self):
        """Testing `RenderHTML` function with LP schedule
        """
        lps_html = RenderHTML(self.lps_dict, self.SCH_TEMPLATE)
        print(lps_html) # TODO: Scrape and test html output


    def test_RenderHTML_sessions_only(self):
        """Testing `RenderHTML` function - LP schedule - sessions only
        """
        md_content = read_file(path.join('files',
                                         'lp-sch-sessions-only.md'))

        lps_html = RenderHTML(self.markdown(md_content),
                              self.SCH_TEMPLATE)
        print(lps_html) # TODO: Scrape and test html output

    @raises(SystemExit)
    def test_RenderHTML_nonexistent_template(self):
        """Testing `RenderHTML` function - LP schedule - ith non-existent template
        """
        with mock.patch('sys.stdout', new_callable=StringIO) as out:
            nonexistent_template = 'lpsch-template.null'

            lps_html = RenderHTML(self.lps_dict, nonexistent_template)
            expected_out = 'Template %s not found.\n' % template_name
            assert out.getvalue() == expected_out


    def teardown(self):
        """Cleans up things after each test in this class."""
        pass


    @classmethod
    def teardown_class(self):
        """Clean up the mess created by this test."""

        # Remove `speakers.noids` file if it exists.
        if path.isfile('speakers.noids'):
            os.remove('speakers.noids')

        # Change back to the old cwd
        os.chdir(self.old_cwd)


class TestLPSTBA(object):
    """Class tests TBAs in the LP schedule.

    """

    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class.

        """
        # Change current working directory to the tests directory.
        self.old_cwd = os.getcwd()
        os.chdir('tests')

        self.MD_FILE = path.join('files', 'lp-sch-tba.md')
        self.MD_FILE_CONTENT = read_file(self.MD_FILE)

        self.SCH_TEMPLATE = path.join('..', 'libreplanet-templates/2019',
                                      'lp-schedule.jinja2')

        self.markdown = LPSMarkdown()
        self.lps_dict = self.markdown(self.MD_FILE_CONTENT)


    def setup(self):
        """Runs before each test in this class.

        """
        lp_html = RenderHTML(self.lps_dict, self.SCH_TEMPLATE)
        self.soup = BeautifulSoup(lp_html, 'html.parser')


    def cleanup_speaker(self, sp):
        return ' '.join([s.strip() for s in sp.string.split('\n')
                        if len(s.strip())])


    def cleanup_desc(self, desc):
        return desc.replace('\n', '').strip()


    def test_LP_speakers(self):
        """Tests the non-existence of `SpeakerTBA` in gen. HTML.

        """
        speakers = [
            'Paige Peterson, MaidSoft',
            'George Chriss and others, Kat Walsh (moderator)',
            'Andrew Seeder, Dudley Street Neighborhood Initiative',
            'Marina Zhurakhinskaya, Red Hat',
            'Marianne Corvellec, April and Jonathan Le Lous, April',
            'Scott Dexter and Evan Misshula, CUNY, and Erin Glass, UCSD',
            'Michaela R. Brown',
        ]

        for sp in self.soup.find_all(class_='program-session-speaker'):
            sp_block = self.cleanup_speaker(sp)
            assert_equal(sp_block, speakers.pop(0))


    def test_LP_room(self):
        """Tests the non-existence of `RoomTBA` in gen. HTML.

        """
        rooms = [
            'Room 32-141',
            'Room 32-144',
            'Room 31-123',
            'Room 32-144',
            'Room 42-042',
        ]

        for sp in self.soup.find_all(class_='room'):
            room_block = sp.string
            assert_equal(room_block, rooms.pop(0))


    def test_LP_description(self):
        """Tests the non-existence of `DescTBA` in gen. HTML.
        """
        descriptions = [
            'Your workplace can exert a lot of control over how',
            'Free software developers and users tend to be most',
            'This talk will help you gather information, frame',
            'A look back at free software history',
            'Academic Institutions and their researchers',
            'At CUNY, we have taken steps to change this',
            'Being a free software user isn\'t easy,',
            'In this session, I\'ll give students tips',
        ]

        for descs in self.soup.find_all(class_='session-desc'):
            for desc in descs.strings:
                desc = self.cleanup_desc(desc)
                if desc:
                    assert desc.startswith(descriptions.pop(0))


    def teardown(self):
        """Cleans up things after each test in this class.

        """
        # Remove `speakers.noids` file if it exists.
        if path.isfile('speakers.noids'):
            os.remove('speakers.noids')


    @classmethod
    def teardown_class(self):
        """Cleans up the mess after running all tests in this class.
        """
        # Change back to the old cwd
        os.chdir(self.old_cwd)


class TestLPSpeakers(object):
    """
    Class that tests everything related LP Speakers
    """

    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class."""

        # Change current working directory to the tests directory.
        self.old_cwd = os.getcwd()
        os.chdir('tests')

        self.MD_FILE = path.join('files', 'lp-speakers.md')
        self.MD_FILE_CONTENT = read_file(self.MD_FILE)

        self.SPEAKERS_TEMPLATE = path.join('..', 'libreplanet-templates/2016',
                                           'lp-speakers.jinja2')

        self.markdown = LPSpeakersMarkdown()
        self.lpspeakers_dict = self.markdown(self.MD_FILE_CONTENT)


    def setup(self):
        """Runs before each test in this class."""
        pass


    def test_speakers_id_file_exists(self):
        """
        Testing if LPSpeakersMardown created speakers.ids file.
        """
        speakers_ids = self.markdown.speakers_renderer.speakers_ids

        assert path.isfile('speakers.ids')
        assert_equal(json_read('speakers.ids'), speakers_ids)


    def test_LPSpeakersMarkdown_keynotespeakers_name(self):
        """Testing LPSpeakersMarkdown keynote speakers' names.

        """
        keynote_speakers = ['Daniel Kahn Gillmor',
                            'Edward Snowden',
                            'Richard Stallman',
                            'Clara Snowden',
                            'Ludovic Courtès']

        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            assert_equal(kspeaker['speaker'], keynote_speakers[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_id(self):
        """Testing LPSpeakersMarkdown keynote speakers' id.

        """
        keynote_speaker_ids = ['gillmor',
                               'snowden',
                               'stallman',
                               'clara_snowden',
                               'courtes']


        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            assert_equal(kspeaker['id'], keynote_speaker_ids[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_imgurl(self):
        """Testing LPSpeakersMarkdown keynote speakers' image url.

        """
        keynote_speaker_img_urls = [
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/dkg.jpg',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/snowden.jpg',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/stallman.jpg',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/c_snowden.jpg'
        ]



        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            if 'img_url' in kspeaker:
                assert_equal(kspeaker['img_url'],
                             keynote_speaker_img_urls[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_imgalt(self):
        """Testing LPSpeakersMarkdown keynote speakers' image alt text.

        """
        keynote_speaker_img_alts = ['Daniel Kahn Gillmor - Photo',
                                    'Edward Snowden - Photo',
                                    'Richard Stallman - Photo',
                                    '']



        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            if 'img_alt' in kspeaker:
                assert_equal(kspeaker['img_alt'],
                             keynote_speaker_img_alts[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_bio(self):
        """Testing LPSpeakersMarkdown keynote speakers' bio.

        """
        keynote_speaker_bios = [
            ['Daniel Kahn Gillmor is a technologist with the ACLU\'s Speech, Privacy'],
            ['Edward Snowden is a former intelligence officer who served the CIA,'],
            ['Richard is a software developer and software freedom activist. In 1983',
             'Since the mid-1990s, Richard has spent most of his time in political',],
            [],
            ['Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam',
             'Ut turpis felis, pulvinar a semper sed, adipiscing id']
        ]

        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            if 'bio' in kspeaker:
                j = 0
                for p in kspeaker['bio']:
                    p.startswith(keynote_speaker_bios[i][j])
                    j = j + 1

            i = i + 1


    def test_LPSpeakersMarkdown_speakers_name(self):
        """Testing LPSpeakersMarkdown speakers' names.

        """
        speakers = ['Emmanuel',
                    'George Chriss',
                    'Marianne Corvellec',
                    'Richard Fontana',
                    'Mike Gerwitz',
                    'Bassam Kurdali',
                    'Jonathan Le Lous',
                    'M. C. McGrath',
                    'Deb Nicholson',
                    'Stefano Zacchiroli']

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            assert_equal(kspeaker['speaker'], speakers[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_id(self):
        """Testing LPSpeakersMarkdown speakers' id.

        """
        speaker_ids = ['emmanuel',
                       'chriss',
                       'corvellec',
                       'fontana',
                       'gerwitz',
                       'kurdali',
                       'lous',
                       'mcgrath',
                       'nicholson',
                       'zacchiroli']

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            assert_equal(kspeaker['id'], speaker_ids[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_imgurl(self):
        """Testing LPSpeakersMarkdown speakers' image url.

        """
        speaker_img_urls = [
            '', '',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/corvellec.jpg',
            '', '',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/kurdali.png',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/lelous.jpg',
            '',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/nicholson.jpg',
            '//static.fsf.org/nosvn/libreplanet/speaker-pics/zacchiroli.jpg'
        ]

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            if 'img_url' in kspeaker:
                assert_equal(kspeaker['img_url'],
                             speaker_img_urls[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_imgalt(self):
        """Testing LPSpeakersMarkdown speakers' image alt text.

        """
        speaker_img_alts = [
            '', '',
            'Marianne Corvellec - Photo',
            '', '',
            'Bassam Kurdali - Photo',
            'Jonathan Le Lous - Photo',
            '',
            'Deb Nicholson - Photo',
            'Stefano Zacchiroli - Photo']

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            if 'img_alt' in kspeaker:
                assert_equal(kspeaker['img_alt'],
                             speaker_img_alts[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_bio(self):
        """Testing LPSpeakersMarkdown speakers' bio.

        """
        speaker_bios = [
            ['Emmanuel is a Division III student at Hampshire College, studying how'],
            [],
            ['Marianne Corvellec has been a Free Software activist with April'],
            ['Richard Fontana is a lawyer at Red Hat. He leads support for Red Hat\'s'],
            [],
            ['Bassam is a 3D animator/filmmaker whose 2006 short, Elephants Dream,'],
            ['Jonathan has been involved with the Free Software Movement for ten'],
            ['M. C. is the founder of Transparency Toolkit, a free software project'],
            [],
            ['Stefano Zacchiroli is Associate Professor of Computer Science at']
        ]

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            if 'bio' in kspeaker:
                j = 0
                for p in kspeaker['bio']:
                    p.startswith(speaker_bios[i][j])
                    j = j + 1

            i = i + 1


    def test_RenderHTML(self):
        """Testing `RenderHTML` function with LP speakers
        """
        lps_html = RenderHTML(self.lpspeakers_dict, self.SPEAKERS_TEMPLATE)
        print(lps_html) # TODO: Scrape and test html output.


    def teardown(self):
        """Cleans up things after each test in this class."""
        pass


    @classmethod
    def teardown_class(self):
        """Purge the mess created by this test."""

        # Remove `speakers.ids` file if it exists.
        if path.isfile('speakers.ids'):
            os.remove('speakers.ids')

        # Change back to the old cwd
        os.chdir(self.old_cwd)


class TestSpeakersAutoLinking(object):
    """Class tests autolinking of speakers in sessions MD.
    """
    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class."""

        # Change current working directory to the tests directory.
        self.old_cwd = os.getcwd()
        os.chdir('tests')

        self.ids_filename = 'speakers.ids'
        self.noids_filename = 'speakers.noids'

        self.SPEAKERS_MD = path.join('files', 'lp-speakers-autolink.md')
        self.SPEAKERS_MD_CONTENT = read_file(self.SPEAKERS_MD)
        self.SPEAKERS_TEMPLATE = path.join('..', 'libreplanet-templates/2016',
                                           'lp-speakers.jinja2')

        self.SESSIONS_MD = path.join('files', 'lp-sessions-autolink.md')
        self.SESSIONS_MD_CONTENT = read_file(self.SESSIONS_MD)
        self.SESSIONS_TEMPLATE = path.join('..', 'libreplanet-templates/2019',
                                           'lp-schedule.jinja2')


    def setup(self):
        """Runs before each test in this class."""
        pass


    def test_sessions_autolinking(self):
        """Testing autolinking of speakers in sessions. """
        self.speakers_markdown = LPSpeakersMarkdown()
        self.lpspeakers_dict = self.speakers_markdown(
            self.SPEAKERS_MD_CONTENT)

        assert (path.isfile(self.ids_filename) and
                json.loads(read_file(self.ids_filename)))

        self.sessions_markdown = LPSMarkdown()
        self.lps_dict = self.sessions_markdown(self.SESSIONS_MD_CONTENT)

        assert (path.isfile(self.noids_filename) and
                json.loads(read_file(self.noids_filename)))

        speakers = [
            [
                '<a href="speakers.html#snowden">Edward Snowden</a>',
                '<a href="speakers.html#gillmor">Daniel Kahn Gillmor</a>',
            ],
            [
                '<a href="speakers.html#nicholson">Deb Nicholson</a>',
                '<a href="speakers.html#fontana">Richard Fontana</a>',
            ],
            [
                'Paige Peterson', 'MaidSoft'
            ],
            [
                'George Chriss',
                'Kat Walsh (moderator)',
            ],
            [
                '<a href="speakers.html#zacchiroli">Stefano Zacchiroli</a>',
                'Debian', 'OSI', 'IRILL'
            ],
            [
                '<a href="speakers.html#corvellec">Marianne Corvellec</a>',
                'April and Jonathan Le Lous',
                'April'
            ],
            [
                '<a href="speakers.html#brown">Michaela R. Brown</a>',
            ],
            [
                '<a href="speakers.html#gott">Molly Gott</a>'
            ],
            [
                'Christopher Webber',
                '<a href="speakers.html#thompson">David Thompson</a>',
                'Ludovic Courtès',
            ],
        ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['speakers'], speakers[i])
                    i = i + 1

        speakers_noids = [
            'Paige Peterson',
            'George Chriss',
            'Kat Walsh',
            'Jonathan Le Lous',
            'Christopher Webber',
            'Ludovic Courtès',
        ]
        assert_equal(json_read(self.noids_filename), speakers_noids)


    def test_sessions_autolinking_nospeakerids(self):
        """Testing autolinked speakrs in sessions MD when speakers.id not available. """

        assert not path.isfile(self.ids_filename)

        self.sessions_markdown = LPSMarkdown()
        self.lps_dict = self.sessions_markdown(self.SESSIONS_MD_CONTENT)

        assert (path.isfile(self.noids_filename) and
                json.loads(read_file(self.noids_filename)))

        speakers = [
            [
                'Edward Snowden',
                'Daniel Kahn Gillmor',
            ],
            [
                'Deb Nicholson',
                'Richard Fontana',
            ],
            [
                'Paige Peterson', 'MaidSoft'
            ],
            [
                'George Chriss',
                'Kat Walsh (moderator)',
            ],
            [
                'Stefano Zacchiroli',
                'Debian', 'OSI', 'IRILL'
            ],
            [
                'Marianne Corvellec',
                'April and Jonathan Le Lous',
                'April'
            ],
            [
                'Michaela R. Brown',
            ],
            [
                'Molly Gott'
            ],
            [
                'Christopher Webber',
                'David Thompson',
                'Ludovic Courtès',
            ],
        ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['speakers'], speakers[i])
                    i = i + 1

        speakers_noids = [
            'Edward Snowden',
            'Daniel Kahn Gillmor',
            'Deb Nicholson',
            'Richard Fontana',
            'Paige Peterson',
            'George Chriss',
            'Kat Walsh',
            'Stefano Zacchiroli',
            'Marianne Corvellec',
            'Jonathan Le Lous',
            'Michaela R. Brown',
            'Molly Gott',
            'Christopher Webber',
            'David Thompson',
            'Ludovic Courtès',
        ]

        assert_equal(json_read(self.noids_filename), speakers_noids)


    def teardown(self):
        """Cleans up things after each test in this class."""
        # Remove `speakers.ids` file if it exists.
        if path.isfile(self.ids_filename):
           os.remove(self.ids_filename)

        # Remove `speakers.noids` file if it exists.
        if path.isfile(self.noids_filename):
           os.remove(self.noids_filename)


    @classmethod
    def teardown_class(self):
        """Clean up the mess created by this test class"""
        # Change back to the old cwd
        os.chdir(self.old_cwd)
