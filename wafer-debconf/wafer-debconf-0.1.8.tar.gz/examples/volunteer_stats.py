from collections import defaultdict

from django.utils.timezone import now

from volunteers.models import Volunteer
from register.models import Attendee


issued = {
 'Cathylafourmi',
 'KristiProgri',
 'PotatoFormula',
 'aeb',
 'ajfus',
 'andi',
 'arthurmde',
 'cate',
 'cherubin',
 'helen.fornazier',
 'hpdang',
 'jcc',
 'jmw',
 'kanashiro',
 'kobla',
 'kroeckx',
 'lfilipoz',
 'mariobehling',
 'medicalwei-guest',
 'nattie',
 'olasd',
 'onovy',
 'owlfox',
 'philh',
 'phls-guest',
 'piotr',
 'pollo',
 'sheldon_knuth',
 'siqueira',
 'stefanor',
 'taffit',
 'tobi',
 'tzafrir',
 'urbec',
 'valessio-guest',
 'whalebox4.5',
 'zobel',
 'zumbi',
}

def new_shirts():
    volunteers = []
    by_size = defaultdict(list)

    for volunteer in Volunteer.objects.select_related(
                'user',
                'user__attendee',
                'user__userprofile',
            ).all():
        user = volunteer.user
        try:
            attendee = user.attendee
        except Attendee.DoesNotExist:
            continue

        v = {
            'username': user.username,
            'name': user.userprofile.display_name(),
            'shirt_size': attendee.t_shirt_size,
            'tasks': 0
        }
        for task in volunteer.tasks.all():
            template = task.template
            if not template or not template.video_task:
                continue
            if task.start > now():
                continue
            v['tasks'] += 1

        if v['tasks']:
            volunteers.append(v)
        if v['tasks'] >= 3 and v['username'] not in issued:
            by_size[v['shirt_size']].append(v['username'])

    volunteers.sort(key=lambda v: v['tasks'], reverse=True)
    print(by_size)
