#!/usr/bin/env python
# -*- coding: utf-8 -*-
from slackclient import SlackClient
from google_sheets import GoogleSheets
from datetime import datetime
import time
import sys

msg_on_approve = '''```Approve: Поздравляем! Тестировщику понравился билд *{}* и он готов к отправке дальше.
{}, пожалуйста позаботься о его дальнейшей судьбе и смени статус.
{}```'''

msg_on_disapprove = '''```Disapprove: Ой-ой. Тестировщикам что-то не понравилось в *{}*.
{}, разберись с проблемой срочно!
{}```'''

msg_on_long_testing = '''```Тестировщики долго не отвечают по проекту *{}*.
{} разберись с проблемой срочно!
{}```'''

msg_on_long_review = '''```Билд *{}* давно протестирован, но все еще находится в статусе *Review*.
{}, разберись с проблемой срочно!
{}```'''

msg_on_unknown_status = '''```Кто-то очень ошибся и выставил неправильный статус *{3}* тестирования в *{0}*.
{1}, разберись с проблемой срочно!
{2}```'''

msg_on_overdue_milestone = '''```Overdue Milestone: ВНИМАНИЕ! Коллеги, у вас вчера был Milestone *{0}*. Задачи из него не выполнены.
{2}, срочно отдай отчёт по проекту и обсуди с командой дату нового milestone.
Описание milestone {1}
{3}```'''

msg_on_notify_milestone = '''```Напоминание по проекту *{}* Дата milestone: {}
Менеджер проекта {}
Описание:
{}
```'''


class Slack:

    def __init__(self):
        self.token = 'xoxp-185515669264-199828799040-278419184210-9f16965b9abba9335abe137d67065540'
        self.user = 'USLACKBOT'
        self.slack_client = SlackClient(self.token)
        self.api_call = self.slack_client.api_call("im.list")

    def send_message(self, channel, message, as_bot=True, username='The Better Manager'):
        self.slack_client.api_call('chat.postMessage', link_names=1, channel=channel, text=message,
                                   as_user=not as_bot, icon_emoji=':robot_face:', username=username)


class GoogleParser:

    def __init__(self, slack, debug_mode=False):
        self.slack = slack
        self.debug_mode = debug_mode
        self.gs = GoogleSheets(CLIENT_SECRET_FILE='google_drive_client_secret.json')
        self.gs.set_document('1RVZg7PoqMS0ON-fg1QjfnY5LRczQSS_jsxrZrCEu6lA')
        self.range_testing = self.gs.read_range('Testing Statuses', 'A1', 'L')
        self.range_milestones = self.gs.read_range('Milestones From Form', 'A1', 'L')
        self.range_common = self.gs.read_range('SlackBot', 'A1', 'C')
        self.managers = {}
        self.channels = {}
        self.parse_managers()

    def parse_managers(self):
        for i, row in enumerate(self.range_common):
            project = row[0]
            if not project:
                continue
            self.channels[project] = row[1]
            self.managers[project] = row[2]

    def get_slack_manager_of_project(self, project):
        if project not in self.managers:
            msg = 'Project [{}] not in self.managers'
            Slack().send_message('@volodar', msg)
        return self.managers[project] if not self.debug_mode else 'volodar'

    def get_slack_channel_of_project(self, project):
        if project not in self.channels:
            msg = 'Project [{}] not in self.channels'
            Slack().send_message('@volodar', msg)
        return self.channels[project] if not self.debug_mode else 'volodar'

    def get_slack_channel_general(self):
        return '#general' if not self.debug_mode else '@volodar'

    @staticmethod
    def get_header(range):
        header = range[0]
        range = range[1:]
        return header, range

    @staticmethod
    def get_value(header, row, name):
        index = header.index(name)
        return row[index]

    @staticmethod
    def convert_data(date):
        m, d, t = date.split('/')
        human = '{}.{}.{}'.format(d, m, t)
        return human

    def send_notification_testing_status(self, header, row):
        status = GoogleParser.get_value(header, row, 'Status').encode('utf-8')
        if not status:
            return
        project = GoogleParser.get_value(header, row, 'Project Name').encode('utf-8')
        comment = GoogleParser.get_value(header, row, 'Comments').encode('utf-8')
        manager = self.get_slack_manager_of_project(project)
        channel = self.get_slack_channel_of_project(project)
        messages = {
            'Approve': msg_on_approve,
            'Disapprove': msg_on_disapprove,
            'Review': msg_on_long_review,
            # '': msg_on_long_testing,
            'x': msg_on_unknown_status,
        }

        slack_message = messages[status] if status in messages else messages['x']
        slack_message = slack_message.format(project, manager, comment, status)
        self.slack.send_message(channel, slack_message)
        # self.slack.send_message(self.get_slack_channel_general(), slack_message)

    def warning_testing_statuses(self):
        header, range = GoogleParser.get_header(self.range_testing)
        for row in range:
            project = GoogleParser.get_value(header, row, 'Project Name')

            if not project:
                continue
            status = GoogleParser.get_value(header, row, 'Status')
            if status == 'Approve':
                self.send_notification_testing_status(header, row)
            elif status == 'Disapprove':
                self.send_notification_testing_status(header, row)
            elif status == '' or status == 'Review':
                time_of_request = GoogleParser.get_value(header, row, 'Timestamp')
                try:
                    time_of_request = time.mktime(datetime.strptime(time_of_request.split(' ')[0], "%m/%d/%Y").timetuple())
                except ValueError:
                    time_of_request = time.mktime(datetime.strptime(time_of_request.split(' ')[0], "%Y-%m-%d").timetuple())

                now = datetime.now()
                now_date = '{}/{}/{}'.format(now.month, now.day, now.year)
                now_time = time.mktime(datetime.strptime(now_date, "%m/%d/%Y").timetuple())
                diff = now_time - time_of_request
                days = diff / (60 * 60 * 24)
                if days > 2 and status == '':
                    self.send_notification_testing_status(header, row)
                if days > 4 and status == 'Review':
                    self.send_notification_testing_status(header, row)
            elif status not in ['Release', 'Review', 'In work']:
                self.send_notification_testing_status(header, row)

    def warning_milestones(self):
        header, range = GoogleParser.get_header(self.range_milestones)
        for row in range:
            project = GoogleParser.get_value(header, row, 'Project')
            if not project:
                continue
            status = GoogleParser.get_value(header, row, 'Status')
            if status in ['Release', 'Done', 'Moved']:
                continue
            finish_date = GoogleParser.get_value(header, row, 'Date')
            finish_time = time.mktime(datetime.strptime(finish_date, "%m/%d/%Y").timetuple())
            now = datetime.now()
            now_date = '{}/{}/{}'.format(now.month, now.day, now.year)
            now_time = time.mktime(datetime.strptime(now_date, "%m/%d/%Y").timetuple())

            overdue = now_time > finish_time
            if overdue:
                manager = self.get_slack_manager_of_project(project).encode('utf-8')
                channel = self.get_slack_channel_of_project(project).encode('utf-8')
                comment = GoogleParser.get_value(header, row, 'Description').encode('utf-8')
                slack_message = msg_on_overdue_milestone
                slack_message = slack_message.format(project, GoogleParser.convert_data(finish_date), manager, comment)
                self.slack.send_message(channel, slack_message)
                # self.slack.send_message(self.get_slack_channel_general(), slack_message)

    def notify_about_milestones(self):
        header, range = GoogleParser.get_header(self.range_milestones)
        for row in range:
            project = GoogleParser.get_value(header, row, 'Project')
            if not project:
                continue
            status = GoogleParser.get_value(header, row, 'Status')
            if status in ['Release', 'Done', 'Moved']:
                continue
            finish_date = GoogleParser.get_value(header, row, 'Date')
            manager = self.get_slack_manager_of_project(project).encode('utf-8')
            comment = GoogleParser.get_value(header, row, 'Description').encode('utf-8')
            channel = self.get_slack_channel_of_project(project).encode('utf-8')
            slack_message = msg_on_notify_milestone
            slack_message = slack_message.format(project, GoogleParser.convert_data(finish_date), manager, comment)
            self.slack.send_message(channel, slack_message)

    def notify_about_milestones_sumary(self):
        range = self.gs.read_range('DashboardJoined', 'A2', 'A2')
        message = range[0][0].encode('utf-8').strip()
        message = '```{}```'.format(message)
        self.slack.send_message('#milestones', message)


def run(event, debug_mode=False):
    try:
        g = GoogleParser(Slack(), debug_mode)
        if event == 'hour':
            g.warning_testing_statuses()
            g.warning_milestones()
        elif event == 'daily':
            g.notify_about_milestones()
            g.notify_about_milestones_sumary()
    except:
        Slack().send_message('@volodar', 'Crash in management bot\n{}'.format(event))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        event = sys.argv[1]
    else:
        event = 'daily'
    run(event)
