from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.db import transaction


from . import record
from . import actions
from . import models


class JournalTestCase(TestCase):
    def setUp(self):
        models.JOURNAL_METADATA_CACHE_TIMEOUT = 0
        self.users = []
        self.groups = []
        with transaction.atomic():
            for i in range(20):
                self.users.append(
                        User.objects.create(username='user%s' % i))
            for i in range(20):
                self.groups.append(
                        Group.objects.create(name='group%s' % i))
            for i in range(20):
                record('login', '{user} logged in', user=self.users[i])
            for i in range(20):
                record('group-changed', '{user1} gave group {group} to {user2}',
                        user1=self.users[i], group=self.groups[i], 
                        user2=self.users[(i+1) % 20])
            for i in range(20):
                record('logout', '{user} logged out', user=self.users[i])

    def test_login(self):
        for i, event in zip(range(20), models.Journal.objects.for_tag('login').order_by('id')):
            self.assertEqual(unicode(event), 'user{0} logged in'.format(i))

    def test_groups(self):
        for i, event in zip(range(40), models.Journal.objects.for_tag('group-changed').order_by('id')):
            self.assertEqual(unicode(event),
                    'user{0} gave group group{0} to user{1}'.format(i, (i+1)%20))

    def test_logout(self):
        for i, event in zip(range(20), models.Journal.objects.for_tag('logout').order_by('id')):
            self.assertEqual(unicode(event), 'user{0} logged out'.format(i))

    def test_export_as_csv(self):
        qs = models.Journal.objects.all()
        l = list(actions.export_as_csv_generator(qs))
        self.assertEquals(set(l[0]), set(['time', 'tag', 'message', 'group', 'group__id', 'user', 'user__id', 'user1', 'user1__id', 'user2', 'user2__id']))
        l = list(actions.export_as_csv_generator(qs[:5]))
        self.assertEquals(set(l[0]), set(['time', 'tag', 'message', 'user', 'user__id']))
        for user in self.users:
            user.delete()
        qs = models.Journal.objects.all()
        l = list(actions.export_as_csv_generator(qs))
        self.assertEquals(l[1]['user'], '<deleted>')

