#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from collections import Counter
from datetime import timedelta

import django
from django.conf import settings
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from common.logger import Log

try:
    from pygraphviz import AGraph
except:
    class AGraph(object):
        def __init__(self, thing=None, filename=None, data=None, string=None, handle=None, name='', strict=True,
                     directed=False, **attr):
            pass

        def add_node(self, n, **attr):
            pass

        def draw(self, path=None, format=None, prog=None, args=''):
            return ''

        def add_edge(self, u, v=None, key=None, **attr):
            pass

        def write(self, path=None):
            pass

log = Log('goflow.workflow.managers')


class Activity(models.Model):
    """Activities represent any kind of action an employee might want to do on an instance.

    The action might want to change the object instance, or simply
    route the instance on a given path. Activities are the places
    where any of these action are resolved by employees.
    """
    KIND_CHOICES = (
        ('standard', 'standard'),
        ('dummy', 'dummy'),
        ('subflow', 'subflow'),
    )
    COMP_CHOICES = (
        ('and', 'and'),
        ('xor', 'xor'),
    )
    title = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, verbose_name='type', default='standard')
    process = models.ForeignKey('Process', related_name='activities', on_delete=models.CASCADE)
    push_application = models.ForeignKey('PushApplication', related_name='push_activities', null=True, blank=True,
                                         on_delete=models.CASCADE)
    pushapp_param = models.CharField(max_length=100, null=True, blank=True,
                                     help_text="parameters dictionary; example: {'username':'john'}")
    application = models.ForeignKey('Application', related_name='activities', null=True, blank=True,
                                    help_text='leave it blank for prototyping the process without coding',
                                    on_delete=models.CASCADE)
    app_param = models.CharField(max_length=300, verbose_name='parameters',
                                 help_text="parameters dictionary; example: { 'form_class': 'imovel.form.ContratoLocForm', 'goto': 'contratoLoc'}",
                                 null=True, blank=True)
    subflow = models.ForeignKey('Process', related_name='parent_activities', null=True, blank=True,
                                on_delete=models.CASCADE)
    roles = models.ManyToManyField(Group, related_name='activities')  # , null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    autostart = models.BooleanField(default=False)
    autofinish = models.BooleanField(default=True)
    sendmail = models.BooleanField(default=True)
    approve = models.BooleanField(default=False, verbose_name='Aprovação',
                                  help_text='É atividade de aprovação/rejeição de workflow?')
    ratify = models.BooleanField(default=False, verbose_name='Ratificação',
                                 help_text='É atividade de ratificação ou homologação do workflow?')
    join_mode = models.CharField(max_length=3, choices=COMP_CHOICES, verbose_name='join mode', default='xor')
    split_mode = models.CharField(max_length=3, choices=COMP_CHOICES, verbose_name='split mode', default='and')

    def nb_input_transitions(self):
        """ returns the number of inputing transitions.
        """
        return Transition.objects.filter(output=self, process=self.process).count()

    def __str__(self):
        # return '%s (%s)' % (self.title, self.process.title)
        return self.title

    class Meta:
        unique_together = (("title", "process"),)
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'


class ProcessManager(models.Manager):
    """Custom model manager for Process
    """

    # TODO: also not too happy about this one.
    def is_enabled(self, title):
        """
        Determines given a title if a process is enabled or otherwise

        :rtype: bool

        usage::

            if Process.objects.is_enabled('leave1'):
                # do something

        """
        return self.get(title=title).enabled

    def check_can_start(self, process_name, user):
        """
        Checks whether a process is enabled and whether the user has permission
        to instantiate it; raises exceptions if not the case, returns None otherwise.

        @type process_name: string
        @param process_name: a name of a process. e.g. 'leave'
        @type user: User
        @param user: an instance of django.contrib.auth.models.User,
                     typically retrieved through a request object.
        @rtype:
        @return: passes silently if checks are met,
                 raises exceptions otherwise.
        """
        if not self.is_enabled(process_name):
            log.error('Processo %s desabilitado.' % process_name)
            raise Exception('Processo %s desabilitado.' % process_name)

        if user.has_perm("workflow.can_instantiate"):
            lst = user.groups.filter(name=process_name)
            if lst.count() == 0 or \
                    (lst[0].permissions.filter(codename='can_instantiate').count() == 0):
                log.error('É necessário permissão para iniciar Processo %s.' % process_name)
                raise Exception('É necessário permissão para iniciar Processo %s.' % process_name)
        else:
            log.error('Permissão é necessária para o processo %s.' % process_name)
            raise Exception('Permissão é necessária.')
        return

    @staticmethod
    def workflow_graph(ftype='svg'):
        """
        Gera o gráfico de todos os processos
        """
        process = Process.objects.all()

        for p in process:
            p.as_graph(ftype=ftype, to_save=True)


class Process(models.Model):
    """A process holds the map that describes the flow of work.

    The process map is made of activities and transitions.
    The instances you create on the map will begin the flow in
    the configured begin activity. Instances can be moved
    forward from activity to activity, going through transitions,
    until they reach the End activity.
    """
    PRIORITY_HIGH = 1
    PRIORITY_NORMAL = 2
    PRIORITY_LOW = 3
    DEFAULT_PRIORITY = PRIORITY_NORMAL

    PRIORITY_CHOICES = (
        (PRIORITY_HIGH, 'Alta'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_LOW, 'Baixa'),
    )

    GOAL_SISTEMA = 1
    GOAL_ATENDIMENTO = 2
    GOAL_CONTRATO_ADM = 3
    GOAL_CONTRATO_LOC = 4

    GOAL_CHOICES = (
        (GOAL_SISTEMA, 'Sistema'),
        (GOAL_ATENDIMENTO, 'Atendimento ao Cliente'),
        (GOAL_CONTRATO_ADM, 'Contrato de Administração'),
        (GOAL_CONTRATO_LOC, 'Contrato de Locação'),
    )

    enabled = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    # description.allow_tags = True
    begin = models.ForeignKey('Activity', related_name='bprocess', verbose_name='initial activity', null=True,
                              blank=True, on_delete=models.CASCADE)
    end = models.ForeignKey('Activity', related_name='eprocess', verbose_name='final activity', null=True, blank=True,
                            help_text='a default end activity will be created if blank', on_delete=models.CASCADE)
    priority = models.IntegerField(default=DEFAULT_PRIORITY, choices=PRIORITY_CHOICES, verbose_name='Prioridade')
    goal = models.IntegerField(default=GOAL_ATENDIMENTO, choices=GOAL_CHOICES, verbose_name='Função')

    # add new ProcessManager
    objects = ProcessManager()

    class Meta:
        verbose_name_plural = 'Processes'
        permissions = (
            ("can_instantiate", "Can instantiate"),
            ("can_browse", "Can browse"),
        )

    def __str__(self):
        return '%s - %s ' % (self.pk, self.title)

    def summary(self):
        return mark_safe('<pre>%s</pre>' % self.description)

    def action(self):
        return mark_safe(
            'add <a href=../activity/add/>a new activity</a> or <a href=../activity/>copy</a> an '
            'activity from another process')

    def add_activity(self, name):
        """
        name: name of activity (get or created)
        """
        a, created = Activity.objects.get_or_create(title=name, process=self,
                                                    defaults={'description': '(add description)'})
        return a

    def add_transition(self, name, activity_out, activity_in):
        t, created = Transition.objects.get_or_create(name=name, process=self,
                                                      output=activity_out,
                                                      defaults={'input': activity_in})
        return t

    def create_authorized_group_if_not_exists(self):
        g, created = Group.objects.get_or_create(name=self.title)
        if created:
            ptype = ContentType.objects.get_for_model(Process)
            cip = Permission.objects.get(content_type=ptype, codename='can_instantiate')
            g.permissions.add(cip)

    def save(self, no_end=False, **kwargs):
        # models.Model.save(self, **kwargs)
        super(Process, self).save(**kwargs)
        # instantiation group
        self.create_authorized_group_if_not_exists()

        if not no_end and not self.end:
            self.end = Activity.objects.create(title='End', process=self, kind='dummy', autostart=True)
            # models.Model.save(self, **kwargs)
            super(Process, self).save(**kwargs)
        try:
            if self.end and self.end.process.id != self.id:
                a = self.end
                a.id = None
                a.process = self
                a.save()
                self.end = a
                # models.Model.save(self)
                super(Process, self).save(**kwargs)
            if self.begin and self.begin.process.id != self.id:
                a = self.begin
                a.id = None
                a.process = self
                a.save()
                self.begin = a
                # models.Model.save(self, **kwargs)
                super(Process, self).save(**kwargs)
        except Exception:
            # admin console error ?!?
            pass

    def as_graph(self, ftype='svg', to_save=False, args=None):
        init = 0
        end = -1
        keys_in = []
        keys_out = []
        trans = []
        # rankdir='LR' -> Left to Right
        # rankdir='TB' -> Top to Bottom , ratio='fill' size='8,8',width='500px', size='8,8' viewport='500,500',
        # g = AGraph(directed=True, rankdir='LR', size='10,10', ratio='auto', splines='line', nodesep=1)
        # g = AGraph(directed=True, rankdir='LR', size='10,10', ratio='auto', splines='ortho', nodesep=1)
        g = AGraph(directed=True, rankdir='LR', size='10,10', ratio='auto', splines='ortho', nodesep=1)

        g.add_node(init, label='', shape='circle', style='filled', color='black', tooltip='')
        g.add_node(end, label='', shape='doublecircle', style='bold', color='black', tooltip='')
        for a in self.activities.all():
            color = 'black'
            if a.pk in args.get('pending'):
                color = 'blue'
            elif a.pk in args.get('problem'):
                color = 'red'
            elif a.pk in args.get('completed'):
                color = 'green'
            g.add_node(a.id, label=a.title, shape='box', style='rounded', color=color, tooltip='')

        for t in self.transitions.all():
            # g.add_edge(t.input.id, t.output.id, label=t.description if t.description else t.name)
            keys_in.append(t.output)
            keys_out.append(t.input)
            trans.append(t)

        k_in = list(Counter(keys_in).keys())
        v_in = list(Counter(keys_in).values())
        for i, val in enumerate(v_in):
            if val > 1:
                if k_in[i].join_mode == 'xor':
                    mode = 'X'
                else:
                    mode = '+'
                g.add_node('IN%s' % k_in[i].id, label=mode, shape='diamond', color='black', tooltip='',
                           constraint='false')

        k_out = list(Counter(keys_out).keys())
        v_out = list(Counter(keys_out).values())
        for i, val in enumerate(v_out):
            if val > 1:
                if k_out[i].split_mode == 'xor':
                    mode = 'X'
                else:
                    mode = '+'
                g.add_node('OUT%s' % k_out[i].id, label=mode, shape='diamond', color='black', tooltip='',
                           constraint='false')

        for t in trans:
            # description = t.description if t.description is not None else t.name if t.name is not None else ''
            description = ''
            # _in = False
            # _out = False
            try:
                if v_out[k_out.index(t.input)] > 1:
                    source = 'OUT%s' % t.input.id
                    g.add_edge(t.input.id, source, xlabel=description, tooltip='')
                    # g.add_edge(t.input.id, source, xlabel=description, splines='ortho', tooltip='', 
                    # tailport='e', headport='w')
                    # _out = True
                else:
                    source = t.input.id
            except Exception as v:
                source = t.input.id
            try:
                if v_in[k_in.index(t.output)] > 1:
                    destination = 'IN%s' % t.output.id
                    g.add_edge(destination, t.output.id, xlabel=description, tooltip='')
                    # g.add_edge(destination, t.output.id, xlabel=description, splines='ortho', tooltip='', 
                    # tailport='e', headport='w')
                    # _in = True
                else:
                    destination = t.output.id
            except Exception as v:
                destination = t.output.id

            # if _in and _out:
            #     g.add_edge(source, destination, xlabel=description, tooltip='', tailport='s', headport='s')
            # else:
            g.add_edge(source, destination, xlabel=description, tooltip='')
            # g.add_edge(source, destination, xlabel=description, splines='ortho', tooltip='')

        try:
            if v_in[k_in.index(self.begin)] > 1:
                destination = 'IN%s' % self.begin.id
            else:
                destination = self.begin.id
        except Exception as v:
            destination = self.begin.id
        g.add_edge(init, destination, tooltip='')
        # g.add_edge(init, destination, splines='ortho', tooltip='')
        try:
            if v_out[k_out.index(self.end)] > 1:
                source = 'OUT%s' % self.end.id
            else:
                source = self.end.id
        except Exception as v:
            source = self.end.id
        g.add_edge(source, end, tooltip='')
        # g.add_edge(source, end, splines='ortho', tooltip='')

        if to_save:
            path = '%s/img/Workflow-%s-%s.%s' % (settings.STATICFILES_DIRS[0], self.id, self.title, ftype)
        else:
            path = None
        s = mark_safe(g.draw(path=path, format=ftype, prog='dot'))
        return s


class Application(models.Model):
    """ An application is a python view that can be called by URL.

        Activities can call applications.
        A commmon prefix may be defined: see settings.WF_APPS_PREFIX
    """
    url = models.CharField(max_length=255, unique=True,
                           help_text='relative to prefix in settings.WF_APPS_PREFIX or URL pattern name')
    # TODO: drop abbreviations (perhaps here not so necessary to ??
    SUFF_CHOICES = (
        ('w', 'workitem.id'),
        ('i', 'instance.id'),
        ('o', 'object.id'),
    )
    suffix = models.CharField(max_length=1, choices=SUFF_CHOICES, verbose_name='suffix', null=True, blank=True,
                              default='w', help_text='http://[host]/[settings.WF_APPS_PREFIX/][url]/[suffix]')
    detected_as_auto = None

    def __str__(self):
        return self.url

    def get_app_url(self, workitem=None, extern_for_user=None):
        def get_workitem_path(wi):
            _path = ''
            if wi:
                if self.suffix:
                    if self.suffix == 'w':
                        _path = '%d/' % wi.id
                    if self.suffix == 'i':
                        _path = '%d/' % wi.instance.id
                    if self.suffix == 'o':
                        # path = '%d/' % (workitem.wfobject().content_object.id)
                        _path = '%d/' % wi.wfobject().id
                else:
                    _path = '?workitem_id=%d' % wi.id
            return _path

        from django.conf import settings
        path = '%s/%s/' % (settings.WF_APPS_PREFIX, self.url)
        if extern_for_user:
            path = 'http://%s%s%s' % (extern_for_user.userprofile.web_host, path, get_workitem_path(workitem))
            # path = 'http://%s%s' % (extern_for_user.get_profile().web_host, path)

        #  Se é o workflow padrão, então usa os dados do WF atual chamando o WF padrão Execute
        # if path == '%s/workflow_execute_std/' % settings.WF_APPS_PREFIX:
        #     path = '/common/workflow/workflow_execute/'

        # try:
        #     # Se o path não existir então tenta se a configuração é de resolve
        #     func, args, kwargs = resolve(path)
        # except Exception as v:
        #     path = reverse(self.url)

        try:
            # func, args, kwargs = resolve(path)
            resolve(path)
        except Exception as v:
            try:
                # func, args, kwargs = resolve(path + '0/')
                resolve(path + '0/')
            except Exception as v:
                try:
                    url = reverse(self.url)
                    # func, args, kwargs = resolve(url)
                    resolve(url)
                    path = url
                except Exception as v:
                    url = reverse(self.url, args=[0])
                    # func, args, kwargs = resolve(url + '0/')
                    resolve(url)
                    path = url

        return path

    def get_handler(self):
        """returns handler mapped to url.
        """
        try:
            func, args, kwargs = resolve(self.get_app_url() + '0/')
            self.detected_as_auto = False
        except Exception as v:
            func, args, kwargs = resolve(self.get_app_url())
            self.detected_as_auto = True
        return func

    def documentation(self):
        doc = ''
        if self.detected_as_auto:
            doc = 'detected as auto application.<hr>'
        try:
            doc += u'<pre>%s</pre>' % self.get_handler().__doc__
        except Exception as v:
            doc += 'WARNING: the url %s is not resolved.' % self.get_app_url()
        return mark_safe(doc)

    def has_test_env(self):
        if Process.objects.filter(title='test_%s' % self.url).count() > 0:
            return True
        return False

    def create_test_env(self, user=None):
        if self.has_test_env():
            return

        g = Group.objects.create(name='test_%s' % self.url)
        ptype = ContentType.objects.get_for_model(Process)
        cip = Permission.objects.get(content_type=ptype, codename='can_instantiate')
        g.permissions.add(cip)
        # group added to current user
        if user:
            user.groups.add(g)

        p = Process.objects.create(title='test_%s' % self.url, description='unit test process')
        p.begin = p.end
        p.begin.autostart = False
        p.begin.title = "test_activity"
        p.begin.kind = 'standard'
        p.begin.application = self
        p.begin.description = 'test activity for application %s' % self.url
        p.begin.save()

        p.begin.roles.add(g)

        p.save()

    def remove_test_env(self):
        if not self.has_test_env():
            return
        Process.objects.filter(title='test_%s' % self.url).delete()
        Group.objects.filter(name='test_%s' % self.url).delete()

    def test(self):
        if self.has_test_env():
            return mark_safe(('<a href=teststart/%d/>start test instances</a> | '
                              '<a href=testenv/remove/%d/>remove unit test env</a>') % (self.id, self.id))
        else:
            return mark_safe('<a href=testenv/create/%d/>create unit test env</a>' % self.id)


class PushApplication(models.Model):
    """A push application routes a workitem to a specific user.
    It is a python function with the same prototype as the built-in
    one below::

        def route_to_requester(workitem):
            return workitem.instance.user

    Other parameters may be added (see Activity.pushapp_param field).
    Built-in push applications are implemented in pushapps module.
    A commmon prefix may be defined: see settings.WF_PUSH_APPS_PREFIX

    """
    url = models.CharField(max_length=255, unique=True)

    def get_handler(self):
        """returns handler mapped to url.
        """
        try:
            # search first in pre-built handlers
            from . import pushapps
            if self.url in dir(pushapps):
                # TODO? Por que? Acho que não, acho que está ok.
                # Acho que o melhor é deixar todos os pushapps no fonte default,
                # pois se não vai ter que tratar prefix.
                return eval('pushapps.%s' % self.url)
            # then search elsewhere
            prefix = settings.WF_PUSH_APPS_PREFIX
            # dyn import
            exec('import %s' % prefix)
            return eval('%s.%s' % (prefix, self.url))
        except Exception as v:
            log.error('PushApplication.get_handler %s', v)
        return None

    def documentation(self):
        return mark_safe('<pre>%s</pre>' % self.get_handler().__doc__)

    def execute(self, workitem, **kwargs):
        handler = self.get_handler()
        return handler(workitem, **kwargs)

    def __str__(self):
        return self.url

    def test(self):
        return mark_safe('<a href=#>test (not yet implemented)</a>')


class Transition(models.Model):
    """ A Transition connects two Activities: a From and a To activity.

    Since the transition is oriented you can think at it as being a
    link starting from the From and ending in the To activity.
    Linking the activities in your process you will be able to draw
    the map.

    Each transition is associated to a condition that will be tested
    each time an instance has to choose which path to follow.
    If the only transition whose condition is evaluated to true will
    be the transition choosen for the forwarding of the instance.
    """
    name = models.CharField(max_length=50, null=True, blank=True)
    process = models.ForeignKey(Process, related_name='transitions', on_delete=models.CASCADE)
    input = models.ForeignKey(Activity, related_name='transition_inputs', on_delete=models.CASCADE)
    condition = models.CharField(max_length=200, null=True, blank=True,
                                 help_text='ex: instance.condition=="OK" | OK')
    output = models.ForeignKey(Activity, related_name='transition_outputs', on_delete=models.CASCADE)
    description = models.CharField(max_length=100, null=True, blank=True,
                                   help_text='Description will be shown on graph')
    precondition = models.CharField(max_length=200, null=True, blank=True,
                                    help_text='object method that return True if transition is possible. '
                                              'ex.: obj.is_ok()')

    def is_transition(self):
        """ used in admin templates.
        """
        return True

    def save(self, **kwargs):
        if self.input.process != self.process or self.output.process != self.process:
            raise Exception("a transition and its activities must be linked to the same process")
        # models.Model.save(self, **kwargs)
        super(Transition, self).save(**kwargs)

    def __str__(self):
        return self.name or 't%s' % str(self.pk)

    class Meta:
        pass
        # unique_together = (("input", "condition"),)


class UserProfile(models.Model):
    """Contains workflow-specific user data.

    It has to be declared as auth profile module as following:
    settings.AUTH_PROFILE_MODULE = 'workflow.userprofile'

    If your application have its own profile module, you must
    add to it the workflow.UserProfile fields.
    """
    # user = models.ForeignKey(User, unique=True)  # NOQ
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    web_host = models.CharField(max_length=100, default='localhost:8000')
    notified = models.BooleanField(default=True, verbose_name='notification by email')
    last_notif = models.DateTimeField(default=django.utils.timezone.now)
    nb_wi_notif = models.IntegerField(default=1, verbose_name='items before notification',
                                      help_text='notification if the number of items waiting is reached')

    notif_delay = models.IntegerField(default=1, verbose_name='Notification delay', help_text='in days')
    urgent_priority = models.IntegerField(default=5, verbose_name='Urgent priority threshold',
                                          help_text='a mail notification is sent when an item has at least '
                                                    'this priority level')

    def save(self, **kwargs):
        if not self.last_notif:
            self.last_notif = django.utils.timezone.now()
        # models.Model.save(self, **kwargs)
        super(UserProfile, self).save(**kwargs)

    def check_notif_to_send(self):
        if django.utils.timezone.now() > self.last_notif + timedelta(days=self.notif_delay or 1):
            return True
        return False

    def notif_sent(self):
        self.last_notif = django.utils.timezone.now()
        self.save()

    class Meta:
        verbose_name = 'Workflow user profile'
        verbose_name_plural = 'Workflow users profiles'

# ProcessManager.workflow_graph()
