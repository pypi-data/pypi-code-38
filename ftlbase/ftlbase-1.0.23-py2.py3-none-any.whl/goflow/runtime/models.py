#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# from datetime import datetime, timezone  # , timedelta
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from common.logger import Log
from goflow.workflow.models import Process, Activity, Transition, UserProfile
from goflow.workflow.notification import send_mail

log = Log('goflow.runtime.managers')


class InvalidWorkflowStatus(Exception):
    """The requested workitem has invalid status to be used"""
    workitem = None

    def __init__(self, workitem, *args, **kwargs):  # real signature unknown
        super(InvalidWorkflowStatus, self).__init__(*args, **kwargs)
        self.workitem = workitem


class ProcessInstanceManager(models.Manager):
    """Custom model manager for ProcessInstance
    """

    @staticmethod
    def start(process_name, request, item, title=None, priority=None):
        """
        Returns a workitem given the name of a preexisting enabled Process
        instance, while passing in the id of the user, the contenttype
        object and the title.

        :type process_name: string
        :param process_name: a name of a process. e.g. 'leave'
        :type request: request
        :param request: request object.
        :type item: ContentType
        :param item: a content_type object e.g. an instance of LeaveRequest
        :type: title: string
        :param title: title of new ProcessInstance instance (optional)
        :type: priority: integer
        :param priority: default priority (optional)
        :rtype: WorkItem
        :return: a newly configured workitem sent to auto_user,
                 a target_user, or ?? (roles).

        usage::

            wi = Process.objects.start(process_name='leave',
                                       user=admin, item=leaverequest1)

        """

        process = Process.objects.get(title=process_name, enabled=True)
        if priority is None:
            try:
                priority = item.get_priority()
            except Exception as v:
                priority = process.priority

        if not title or (title == 'instance'):
            title = '%s %s' % (process_name, str(item))

        user = request.user

        instance = ProcessInstance.objects.create(process=process, user=user, title=title, content_object=item)
        # instance running
        instance.set_status(ProcessInstance.STATUS_PENDING)

        workitem = WorkItem.objects.create(instance=instance, user=user,
                                           activity=process.begin, priority=priority)
        log.event('created by ' + user.username, workitem)
        log.debug('process:', process_name, 'user:', user.username, 'item:', item)

        wi_next = workitem.process(request)

        return wi_next

    @staticmethod
    def _filter_qs(status=None, notstatus=None, noauto=True, goal=None):
        """ Filter according parameters
        :type status: string
        :param status: filter on status (default=all)
        :type notstatus: string or tuple
        :param notstatus: list of status to exclude (default: [blocked, suspended, fallout, complete])
        :type noauto: bool
        :param noauto: if True (default) auto activities are excluded.
        """
        q = Q()
        if status:
            q &= Q(status__in=status)
        if notstatus:
            q &= ~Q(status__in=notstatus)
        if noauto:
            q &= Q(workitems__activity__autostart=False)
        if goal:
            # process_filter = Process.objects.filter(goal=goal)
            # query = query.filter(instance__process__in=process_filter)
            q &= Q(process__goal__in=goal)
        return q

    @staticmethod
    def list_safe(user, my_work=False, process_pk=None, status=None, notstatus=None, roles=True, withoutrole=True,
                  noauto=True, goal=None):
        """
        Returns a workitem given the name of a preexisting enabled Process
        instance, while passing in the id of the user, the contenttype
        object and the title.

        :type user: User
        :param user: an instance of django.contrib.auth.models.User,
                     typically retrieved through a request object.
        :param process_pk: Name of Process
        :param goal: filter for goal
        :return:

        usage::
            process = Process.objects.start(process_name='atendimento', user=admin)
        """
        if process_pk:
            queryset = ProcessInstance.objects.filter(process__pk=process_pk)
        else:
            queryset = ProcessInstance.objects.all()

        query = queryset

        if status:
            notstatus = []
        else:
            if notstatus is None:
                notstatus = WorkItem.STATUS_CLOSED

        q = ProcessInstanceManager._filter_qs(status=status, notstatus=notstatus, noauto=noauto, goal=goal)

        if user:
            # query = query.filter(user=user)  # , activity__process__enabled=True)
            # q &= Q(user=user)  # , activity__process__enabled=True)
            q &= Q(workitems__user=user)
            # query = query._filter_qs(query, status, notstatus, noauto, goal)
            if my_work:
                groups = Group.objects.none()
            else:
                groups = user.groups.all()
        else:
            query = set([])
            groups = Group.objects.all()

        query = query.filter(q)

        # search pullable workitems if roles enables
        #     Seleciona todos os elegíveis para a role do grupo
        if roles:
            # Cria filtro com todos os grupos que o usuário tem acesso
            qf = Q()
            for role in groups:
                qf |= Q(workitems__pull_roles=role)

            # Seleciona todos os elegíveis para a role do grupo ou os que não tem roles e sem usuário
            qf &= Q(workitems__user__isnull=True, workitems__activity__process__enabled=True)
            qf &= ProcessInstanceManager._filter_qs(status=status, notstatus=notstatus, noauto=noauto, goal=goal)
            # qry = queryset.objects.filter(workitems__user__isnull=True,
            #                               workitems__activity__process__enabled=True)
            # pullables = qry.filter(qf)
            # pullables = WorkItemManager._filter_qs(pullables, status, notstatus, noauto, noauto=noauto, goal=goal)
            pullables = queryset.filter(qf)
            # pullables = WorkItemManager._query_roles(groups, status, notstatus, noauto, noauto=noauto, goal)
            query |= pullables

        # search workitems pullable by anybody
        if withoutrole:
            pullables = ProcessInstance.objects.filter(workitems__pull_roles__isnull=True,
                                                       workitems__user__isnull=True,
                                                       workitems__activity__process__enabled=True)
            log.debug('anybody\'s workitems: %s', str(pullables))
            query |= pullables
            pullables = ProcessInstance.objects.filter(workitems__pull_roles__isnull=True,
                                                       workitems__user__isnull=True,
                                                       workitems__activity__isnull=True)
            log.debug('anybody\'s workitems: %s', str(pullables))
            query |= pullables

        # return list(query)
        query = query.order_by('pk').distinct('pk')
        log.debug('ProcessInstance:', query, 'user:', user.username)
        # return sorted(query, key=lambda instance: instance.content_object.prioridade)
        return sorted(query, key=lambda instance: instance.content_object.pk)

        # return instances

    @staticmethod
    def all_safe(user, goal=None, my_work=False, pending=False, news=False):
        """
        Returns ProcessInstance filtered according parameters

        :type user: User
        :param user:
        :return:

        """

        if pending or news:
            pending_s = 'rp.status NOT IN {0} AND'.format(ProcessInstance.STATUS_CLOSED)
        else:
            pending_s = ''
        goal_s = "AND p.goal='{0}'".format(goal) if goal else ''
        if news:
            news_true = ''
            news_false = '1=0 AND'
            news_w_status = 'rw.status IN {0} AND'.format(ProcessInstance.STATUS_CLOSED)
        else:
            news_true = 'rw.user_id={0} OR'.format(user.pk)
            news_false = ''
            news_w_status = ''

        # print('pending_s=', pending_s, 'goal_s=', goal_s, 'news_true=', news_true, 'news_w_status=', news_w_status,
        #       'news_false=', news_false)

        if my_work:
            query = '''
SELECT rp.*
       , p.goal as goal
       , wa.title as activity
       , (case when rw.status not in {0} then rw.status when rp.status <> '{1}' then '{2}' else NULL end) as activity_status
       , rw.priority as priority
       , (case when rw.status = '{1}' then NULL else u.username end) as user_name
FROM runtime_processinstance rp
JOIN workflow_process p ON p.id = rp.process_id AND p.enabled
INNER JOIN runtime_workitem rw
        ON rp.id = rw.instance_id
       AND rw.status NOT IN {0}
       AND rw.id in (
            select coalesce(max(w2.id), 0) from runtime_workitem w2 where w2.instance_id = rp.id
           )
       AND rw.user_id = {3}
LEFT OUTER JOIN workflow_activity wa ON wa.id = rw.activity_id
LEFT OUTER JOIN auth_user u ON u.id = rp.user_id
WHERE rp.status NOT IN {0}
                            '''
        else:
            query = '''
SELECT rp.*
       , p.goal as goal
       , wa.title as activity
       , (case when rw.status not in {0} then rw.status when rp.status <> '{1}' then '{2}' else NULL end) as activity_status
       , rw.priority as priority
       , (case when rw.status = '{1}' then NULL else u.username end) as user_name
FROM runtime_processinstance rp
JOIN workflow_process p
  ON p.id = rp.process_id AND p.enabled {4}
LEFT OUTER JOIN runtime_workitem rw
             ON rw.instance_id = rp.id
            AND rw.id in (select coalesce(max(w.id), 0) from runtime_workitem w where w.instance_id = rp.id)
LEFT OUTER JOIN workflow_activity wa ON wa.id = rw.activity_id
LEFT OUTER JOIN auth_user u ON u.id = rp.user_id
WHERE {5}
     ({6}
      (rw.user_id IS NULL
       AND exists (SELECT 1 FROM auth_user_groups gb, workflow_activity_roles ar
                     WHERE ar.activity_id=(CASE WHEN rw.id IS NOT NULL THEN rw.activity_id ELSE p.begin_id END)
                       AND gb.group_id=ar.group_id AND gb.user_id={3}))
   OR ({7}
       exists (SELECT 1 FROM auth_user_groups gb, workflow_activity_roles ar
                     WHERE ar.activity_id=rw.activity_id
                       AND gb.group_id=ar.group_id AND gb.user_id={3}))
   OR ({8}
       exists (SELECT 1 FROM auth_user_groups gb, workflow_activity_roles ar
                     LEFT OUTER JOIN workflow_transition wt ON wt.input_id = rw.activity_id
                     WHERE ar.activity_id=wt.output_id
                       AND gb.group_id=ar.group_id AND gb.user_id={3}))
 )
ORDER BY rp.id
        '''

        query = query.format(ProcessInstance.STATUS_CLOSED, ProcessInstance.STATUS_CONCLUDED,
                             ProcessInstance.STATUS_PENDING, user.pk, goal_s, pending_s,
                             news_true, news_false, news_w_status)

        queryset = ProcessInstance.objects.raw(query)

        return queryset

    @staticmethod
    def get_process_by_instance(instance, process_name=None):
        """
        Returns a ProcessInstance given the object and process_name.

        :param instance: filter for goal
        :param process_name: Name of Process
        :return:

        usage::
            process = Process.objects.start(process_name='atendimento', user=admin)
        """
        if process_name:
            instances = ProcessInstance.objects.filter(process__title=process_name)
        else:
            instances = ProcessInstance.objects.all()

        # Acha o content_type do model
        content_type = ContentType.objects.get_for_model(model=instance._meta.model)

        # Acha o ProcessInstance do model instance, isto é, o controle do workflow dessa instance
        instances = instances.filter(content_type=content_type, object_id=instance.pk).order_by('-pk')

        log.debug('ProcessInstance: get_process_by_instance:', instance, ', instances:', instances)
        return instances


class ProcessInstance(models.Model):
    """ This is a process instance.

    A process instance is created when someone decides to do something,
    and doing this thing means start using a process defined in GoFlow.
    That's why it is called "process instance". The process is a class
    (=the definition of the process), and each time you want to
    "do what is defined in this process", that means you want to create
    an INSTANCE of this process.

    So from this point of view, an instance represents your dynamic
    part of a process. While the process definition contains the map
    of the workflow, the instance stores your usage, your history,
    your state of this process.

    The ProcessInstance will collect and handle workitems (see definition)
    to be passed from activity to activity in the process.

    Each instance can have more than one workitem depending on the
    number of split actions encountered in the process flow.
    That means that an instance is actually the collection of all of
    the instance "pieces" (workitems) that we get from splits of the
    same original process instance.

    Each ProcessInstance keeps track of its history through a graph.
    Each node of the graph represents an activity the instance has
    gone through (normal graph nodes) or an activity the instance is
    now pending on (a graph leaf node). Tracking the ProcessInstance history
    can be very useful for the ProcessInstance monitoring.

    When a process instance starts, the instance has to carry an
    implementation object that contains the application data. The
    specifications for the implementation class is:

    (nothing: now managed by generic relation)

    From the instance, the implementation object is reached as following:
      obj = instance.content_object (or instance.wfobject()).
    In a template, a field date1 will be displayed like this:
      {{ instance.wfobject.date1 }} or {{ instance.content_object.date1 }}

    From the object, instances may be reached with the reverse generic relation:
    the following can be added to the model:
      wfinstances = generic.GenericRelation(ProcessInstance)

    """
    STATUS_INACTIVE = '1'
    STATUS_PENDING = '2'
    STATUS_BLOCKED = '3'  # Não em ProcessInstance, só em Workitem
    STATUS_SUSPENDED = '4'
    STATUS_FALLOUT = '5'  # Não em ProcessInstance, só em Workitem
    STATUS_CONCLUDED = '6'

    STATUS_ALL = (STATUS_INACTIVE, STATUS_PENDING, STATUS_BLOCKED, STATUS_SUSPENDED, STATUS_FALLOUT, STATUS_CONCLUDED)
    STATUS_CLOSED = (STATUS_SUSPENDED, STATUS_FALLOUT, STATUS_CONCLUDED)

    # STATUS_ALL = (STATUS_INACTIVE, STATUS_PENDING, STATUS_SUSPENDED, STATUS_CONCLUDED)
    # STATUS_CLOSED = (STATUS_SUSPENDED, STATUS_CONCLUDED)

    STATUS_CHOICES = (
        (STATUS_INACTIVE, 'Não Alocado'),
        (STATUS_PENDING, 'Pendente'),
        (STATUS_BLOCKED, 'Bloqueado'),  # Não em ProcessInstance, só em Workitem
        (STATUS_SUSPENDED, 'Suspenso'),
        (STATUS_FALLOUT, 'Falha'),  # Não em ProcessInstance, só em Workitem
        (STATUS_CONCLUDED, 'Concluído'),
    )

    title = models.CharField(max_length=100)
    process = models.ForeignKey(Process, related_name='instances', null=True, blank=True, on_delete=models.CASCADE)
    creationTime = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, related_name='instances', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_INACTIVE, db_index=True)
    old_status = models.CharField(max_length=1, choices=STATUS_CHOICES, null=True, blank=True)
    condition = models.CharField(max_length=255, null=True, blank=True)

    # refactoring
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # add new ProcessInstanceManager
    objects = ProcessInstanceManager()

    def wfobject(self):
        return self.content_object

    def workitems_list(self):
        """provide html link to workitems for a process instance in admin change list.
        @rtype: string
        @return: html href link "../workitem/?instance__id__exact=[self.id]&ot=asc&o=0"
        """
        nbwi = self.workitems.count()
        return mark_safe('<a href=../workitem/?instance__id__exact=%d&ot=asc&o=0>%d item(s)</a>' % (self.pk, nbwi))

    def __str__(self):
        return "%s - %s" % (self.pk, self.title)

    def set_status(self, status):
        if status not in [x for x, y in ProcessInstance.STATUS_CHOICES]:
            raise Exception('instance status incorrect :%s' % status)
        self.old_status = self.status
        self.status = status
        self.save()

    def get_activity_status_display(self):
        # Field injected in raw sql queryset
        return dict(WorkItem.STATUS_CHOICES).get(self.activity_status)

    def get_goal_display(self):
        # Field injected in raw sql queryset
        return dict(Process.GOAL_CHOICES).get(self.goal)

    # def get_activity_display(self):
    #     w = self.workitems.last()
    #     return w.activity if w else None
    #
    def get_priority_display(self):
        # Field injected in raw sql queryset
        return dict(Process.PRIORITY_CHOICES).get(self.priority)

    # def get_user_display(self):
    #     w = self.workitems.last()
    #     return w.user if w and w.status not in WorkItem.STATUS_CLOSED else None


class WorkItemManager(models.Manager):
    """Custom model manager for WorkItem
    """
    _last = None

    def get_safe(self, id, user=None, enabled_only=False, status=None):
        """
        Retrieves a single WorkItem instance given a set of parameters

        :type id: int
        :param id: the id of the WorkItem instance
        :type user: User
        :param user: an instance of django.contrib.auth.models.User, typically retrieved through a request object.
        :type enabled_only: bool
        :param enabled_only: implies that only enabled processes should be queried
        :param status: filter for status

        usage::

            workitem = WorkItem.objects.get_safe(id, user=request.user)

        """
        if status is None:
            status = (WorkItem.STATUS_INACTIVE, WorkItem.STATUS_PENDING)
        if enabled_only:
            workitem = self.get(id=id, activity__process__enabled=True)
        else:
            workitem = self.get(id=id)
        workitem.check_workitem(user, status)
        return workitem

    @staticmethod
    def get_process_workitems(pk, user=None):
        """
        Retrieves a single WorkItem instance given a set of parameters

        :return: list of workitems belonging to process instance pk
        :type pk: int
        :param pk: the pk of the ProcessInstance
        :type user: User
        :param user: an instance of django.contrib.auth.models.User,
                     typically retrieved through a request object.

        usage::

            workitem = WorkItem.objects.get_process_workitems(id, processinstance.id, user=request.user)

        """
        workitems = WorkItem.objects.filter(instance__pk=pk).order_by('pk')
        # for workitem in workitems:
        #     if not workitem.check_user(user):
        #         error = 'user %s cannot access workitem %d.' % (user.username, workitem.pk)
        #         log.error('workitem.get_process_workitems: %s' % error)
        #         raise Exception(error)
        return workitems

    @staticmethod
    def _filter_qs(query, status=None, notstatus=None, noauto=True, goal=None):
        """ Filter according parameters
        :type status: string
        :param status: filter on status (default=all)
        :type notstatus: string or tuple
        :param notstatus: list of status to exclude (default: [blocked, suspended, fallout, complete])
        :type noauto: bool
        :param noauto: if True (default) auto activities are excluded.
        """
        if status:
            query = query.filter(status__in=status)
        if notstatus:
            query = query.exclude(status__in=notstatus)
        if noauto:
            query = query.exclude(activity__autostart=True)
        if goal:
            process_filter = Process.objects.filter(goal__in=goal)
            query = query.filter(instance__process__in=process_filter)
        return set(query)

    @staticmethod
    def _query_roles(roles, status=None, notstatus=None, noauto=True, goal=None):
        if roles is not None:
            qf = Q()
            for role in roles.all():
                qf |= Q(pull_roles=role)

            # Seleciona todos os elegíveis para a role do grupo ou os que não tem roles e sem usuário
            query = WorkItem.objects.filter(user__isnull=True, activity__process__enabled=True)
            pullables = query.filter(qf)
            pullables = WorkItemManager._filter_qs(pullables, status, notstatus, noauto, goal=goal)
            # pullables = pullables
        else:
            pullables = []
        log.debug('pullables workitems roles %s: %s', str(roles), str(pullables))
        return set(pullables)

    @staticmethod
    def list_safe(user=None, queryset=None, status=None, notstatus=None, roles=True, withoutrole=True,
                  noauto=True, goal=None):
        """
        Retrieve list of workitems (in order to display a task list for example).

        :return: set
        :type user: User
        :param user: filter on instance of django.contrib.auth.models.User (default=all)
        :type queryset: Queryset
        :param queryset: queryset already treated
        :type status: string
        :param status: filter on status (default=all)
        :type notstatus: string or tuple
        :param notstatus: list of status to exclude (default: [blocked, suspended, fallout, complete])
        :type roles: bool
        :param roles: if show workitems associated with user's roles
        :type withoutrole: bool
        :param withoutrole: list all workitems without role set
        :type noauto: bool
        :param noauto: if True (default) auto activities are excluded.
        :param goal: Lista as functions de processo que serão filtradas

        usage::

            workitems = WorkItem.objects.list_safe(user=me, notstatus='complete', noauto=True)

        """
        if queryset is None:
            queryset = WorkItem.objects

        if status:
            notstatus = []
        else:
            if notstatus is None:
                notstatus = WorkItem.STATUS_CLOSED

        if user:
            query = queryset.filter(user=user, activity__process__enabled=True)  # .order_by('-priority')
            query = WorkItemManager._filter_qs(query, status, notstatus, noauto, goal)
            groups = user.groups.all()
        else:
            query = queryset.none()
            groups = Group.objects.all()

        # search pullable workitems if roles enables
        #     Seleciona todos os elegíveis para a role do grupo
        if roles:
            pullables = WorkItemManager._query_roles(groups, status, notstatus, noauto, goal)
            query |= pullables

        # search workitems pullable by anybody
        if withoutrole:
            pullables = queryset.filter(pull_roles__isnull=True,
                                        user__isnull=True,
                                        activity__process__enabled=True)  # .order_by('-priority')
            log.debug('anybody\'s workitems: %s', str(pullables))
            query |= set(pullables)
            pullables = queryset.filter(pull_roles__isnull=True,
                                        user__isnull=True,
                                        activity__isnull=True)  # .order_by('-priority')
            log.debug('anybody\'s workitems: %s', str(pullables))
            query |= set(pullables)

        # return list(query)
        return sorted(query, key=lambda instance: instance.priority)
        # return query

    @staticmethod
    def notify_if_needed(workitems, users=None, roles=None, subject='message', template='goflow/mail-pending'):
        """ notify user if conditions are fullfilled
            If user is not None and workitems, than send email only to this user.
            If check_notif_to_send, then send all pending emails
            If roles is not None then sent email to all users that belong roles
        """
        # workitems = []
        # if user:
        #     workitems |= WorkItemManager.list_safe(user=user, notstatus=WorkItem.STATUS_CONCLUDED, noauto=True)
        # if roles is not None:
        #     workitems |= WorkItemManager._query_roles(roles, status=None, notstatus=WorkItem.STATUS_CONCLUDED,
        #                                               noauto=True)
        task = None
        if users is not None:
            log.info('notification sent to %s' % [user.username for user in users])
            # Envia email para o usuário específico
            if workitems is not None:
                try:
                    task = send_mail(workitems=workitems, users=users, subject=subject, template=template)
                except Exception as v:
                    log.error('sendmail error: %s' % v)

            # Envia email com lista de todas suas pendências para usuário quando ainda não enviou conforme
            # check_notif_to_send.
            # Seria um email geral do dia com todas as pendências
            for user in users:
                profile = UserProfile.objects.get_or_create(user=user)[0]
                # profile = user.userprofile
                if profile.check_notif_to_send():
                    wis = WorkItemManager.list_safe(user=user, withoutrole=False, noauto=False)
                    if len(wis) >= profile.nb_wi_notif and wis is not None:
                        try:
                            task = send_mail(workitems=wis, users=[user, ],
                                             subject='Workflow: Pendências',
                                             template='goflow/mail-all-pending')
                            profile.notif_sent()
                            log.info('notification sent all pending workitems to %s' % user.username)
                        except Exception as v:
                            log.error('sendmail error: only %s' % v)

        if roles is not None:
            users = User.objects.filter(groups=roles.all())
            # for user in users:
            #     log.info('notification roles sent to %s' % user.username)
            #     task = WorkItemManager.notify_if_needed(workitems=workitems, user=user, roles=None,
            #                                             subject=subject, template=template)
            # log.info('notification roles sent to %s' % [user.username for user in users])
            task = WorkItemManager.notify_if_needed(workitems=workitems, users=users, roles=None,
                                                    subject=subject,
                                                    template=template)
        return task

        # def last(self):
        #     if WorkItemManager._last is None:
        #         print('super')
        #         WorkItemManager._last = super().last()
        #     else:
        #         print('normal')
        #     return WorkItemManager._last


class WorkItem(models.Model):
    """A workitem object represents an activity you are performing.

    An Activity object defines the activity, while the workitem object
    represents that you are performing this activity. So workitem is
    an "instance" of the activity.
    """
    STATUS_INACTIVE = ProcessInstance.STATUS_INACTIVE
    STATUS_PENDING = ProcessInstance.STATUS_PENDING
    STATUS_BLOCKED = ProcessInstance.STATUS_BLOCKED
    STATUS_SUSPENDED = ProcessInstance.STATUS_SUSPENDED
    STATUS_FALLOUT = ProcessInstance.STATUS_FALLOUT
    STATUS_CONCLUDED = ProcessInstance.STATUS_CONCLUDED

    STATUS_ALL = ProcessInstance.STATUS_ALL
    STATUS_CLOSED = ProcessInstance.STATUS_CLOSED

    STATUS_CHOICES = ProcessInstance.STATUS_CHOICES

    date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(User, related_name='workitems', null=True, blank=True, on_delete=models.CASCADE)
    instance = models.ForeignKey(ProcessInstance, related_name='workitems', on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='workitems', on_delete=models.CASCADE)
    workitem_from = models.ForeignKey('self', related_name='workitems_to', null=True, blank=True,
                                      on_delete=models.CASCADE)
    others_workitems_from = models.ManyToManyField('self', related_name='others_workitems_to')
    push_roles = models.ManyToManyField(Group, related_name='push_workitems')  # , null=True, blank=True)
    pull_roles = models.ManyToManyField(Group, related_name='pull_workitems')  # , null=True, blank=True)
    blocked = models.BooleanField(default=False, db_index=True)
    priority = models.IntegerField(choices=Process.PRIORITY_CHOICES, default=Process.DEFAULT_PRIORITY, db_index=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_INACTIVE, db_index=True)

    objects = WorkItemManager()

    def activate(self, request, actor=None):
        """
        changes workitem status to 'active' and logs event, activator

        """
        if actor is None:
            actor = request.user
        self.check_workitem(actor, (WorkItem.STATUS_INACTIVE, WorkItem.STATUS_PENDING))
        if self.status == WorkItem.STATUS_PENDING:
            log.info('activate_workitem actor %s workitem %s already active', actor.username, str(self))
            return
        self.status = WorkItem.STATUS_PENDING
        self.user = actor
        self.save()
        log.info('activate_workitem actor %s workitem %s',
                 actor.username, str(self))
        Event.objects.create(name='activated by %s' % actor.username, workitem=self)

    def process(self, request):
        # Se a instância está concluída, então não faz nada
        if self.instance.status == ProcessInstance.STATUS_CONCLUDED:
            return self

        # Atualiza condição se o submit tem condição diferente da atual
        if request.POST:
            try:
                item = self.instance.wfobject()
                priority = item.get_priority()
                if priority != self.priority:
                    self.priority = priority
                    self.save()
            except Exception as v:
                pass

            submit_value = request.POST.get('save', '')
            if self.instance.condition != submit_value:
                self.instance.condition = submit_value
                self.instance.save()

        activity = self.activity

        if activity.kind == 'dummy':
            log.debug('routing activity', activity.title, 'workitem:', self)
            self.activate(request)

            wi_next = self.complete(request)
            return wi_next

        if activity.autostart:
            log.debug('run auto activity', activity.title, 'workitem:', self)
            self.activate(request)

            if self.exec_auto_application(request):
                log.debug('workitem.exec_auto_application:', self)
                wi_next = self.complete(request)
                return wi_next  # Retorna novo workitem criado no complete ou o mesmo se acabou

            return self

        if activity.push_application:
            target_user = self.exec_push_application()
            log.debug('application pushed to user', target_user.username)
            self.user = target_user
            self.save()

            task = WorkItemManager.notify_if_needed(workitems=[self, ], users=[target_user, ],
                                                    subject='Workflow Push - %s' % self)

            Event.objects.create(name='assigned to %s' % target_user.username, workitem=self, external_task=task)
        else:
            # set pull roles; useful (in activity too)?
            # self.pull_roles = activity.roles.all()  # Deprecated in 2.0
            self.pull_roles.set(activity.roles.all())
            self.save()
            if activity.sendmail:
                WorkItemManager.notify_if_needed(workitems=[self, ], roles=self.pull_roles,
                                                 subject='Workflow - %s' % self)

        if activity.autofinish:
            # Efetua conclusão se condição de encerramento ok e autofinish
            try:
                wi_next = None
                trans = Transition.objects.filter(input=activity).order_by('-pk')
                for t in trans:
                    if self.eval_transition_condition(t):
                        wi_next = self.complete(request)
                return self if wi_next is None else wi_next
            except Exception as v:
                log.info('WorkItem: process: except eval_transition_condition %s' % v)

        return self

    def process_autofinish(self, request, item):
        """
        Faz o tratamento de autofinish, condição de transição e prioridade
        :param request: request
        :param item: Content Object
        """
        # Atualiza condição se o submit tem condição diferente da atual
        if request.POST:
            submit_value = request.POST.get('save', '')
            if self.instance.condition != submit_value:
                self.instance.condition = submit_value
                self.instance.save()

        if self.activity.autofinish:
            try:
                priority = item.get_priority()
                if priority != self.priority:
                    self.priority = priority
                    self.save()
            except Exception as v:
                pass
            # Efetua conclusão se condição de encerramento ok e autofinish
            try:
                trans = Transition.objects.filter(input=self.activity).order_by('-pk')
                for t in trans:
                    if self.eval_transition_condition(t):
                        wi_next = self.complete(request)
            except Exception as v:
                log.info('WorkItem: process: except eval_transition_condition %s' % v)

    def forward(self, request, timeout_forwarding=False, subflow_workitem=None):

        # forward_workitem(workitem, path=None, timeout_forwarding=False, subflow_workitem=None):
        """
        Convenience procedure to forwards workitems to valid destination activities.
        :param request:
        :type timeout_forwarding: bool
        :param timeout_forwarding: a workitem with a time-delay??
        :type: subflow_workitem: WorkItem
        :param subflow_workitem: a workitem associated with a subflow ???
        :return: Workitem
        """
        log.info(u'forward_workitem %s', self.__str__())
        if not timeout_forwarding:
            if self.status != WorkItem.STATUS_CONCLUDED:
                return

        if (self.workitems_to.count() > 0) and not subflow_workitem:
            log.debug('forward_workitem canceled for %s: '
                      'workitem.workitems_to.count()', self.__str__())
            return

        if timeout_forwarding:
            # TODO: Avaliar quando timeout está sendo usado uma vez que não aparece na configuração
            log.info('timeout forwarding')
            Event.objects.create(name='timeout', workitem=self)

        wi_next = None

        for destination in self.get_destinations(timeout_forwarding):
            wi_next = self._forward_workitem_to_activity(request, destination)
            if self.activity.split_mode == 'xor':
                break

        return self if wi_next is None else wi_next

    def _forward_workitem_to_activity(self, request, target_activity):
        """
        Passes the process instance embedded in the given workitem
        to a new workitem that is associated with the destination activity.

        @type target_activity: Activity
        @param target_activity: the activity instance to which the workitem
                                should be forwarded
        @rtype: WorkItem
        @return: a workitem that has been passed on to the next
                 activity (and next user)
        """
        instance = self.instance
        # search a blocked workitem first
        qwi = WorkItem.objects.filter(instance=instance, activity=target_activity, status=WorkItem.STATUS_BLOCKED)
        if qwi.count() == 0:
            wi = WorkItem.objects.create(instance=instance, activity=target_activity, user=None, priority=self.priority)
            created = True
            log.info('forwarded to %s', target_activity.title)
            Event.objects.create(name='creation by %s' % self.user.username, workitem=wi)
            Event.objects.create(name='forwarded to %s' % target_activity.title, workitem=self)
            wi.workitem_from = self
        else:
            created = False
            wi = qwi[0]

        if target_activity.join_mode == 'and':
            nb_input_transitions = target_activity.nb_input_transitions()
            if nb_input_transitions > 1:
                if created:
                    # first workitem: block it
                    wi.block()
                    return
                else:
                    wi.others_workitems_from.add(self)
                    if wi.others_workitems_from.all().count() + 1 < nb_input_transitions:
                        # keep blocked
                        return
                    else:
                        wi.status = WorkItem.STATUS_INACTIVE
                        wi.save()
                        log.info('activity %s: workitem %s unblocked', target_activity.title, str(wi))
        else:
            if not created:
                # join_mode='and'
                log.error('activity %s: join_mode must be and', target_activity.title)
                self.fall_out()
                wi.fall_out()
                return

        wi = wi.process(request)

        return wi

    def complete(self, request, actor=None, priority=None):
        """
        changes status of workitem to 'complete' and logs event
        """
        if actor is None:
            actor = request.user
        self.check_workitem(actor, WorkItem.STATUS_PENDING)
        self.status = WorkItem.STATUS_CONCLUDED
        self.user = actor
        self.save()
        log.info('complete_workitem actor %s workitem %s', actor.username, str(self))
        Event.objects.create(name='completed by %s' % actor.username, workitem=self)

        wi_next = None  # Próximo, se autofinish

        if self.activity.autofinish:
            log.debug('activity autofinish: forward')
            wi_next = self.forward(request)

        # if end activity, instance is complete
        if self.instance.process.end == self.activity or self.instance.process.end == wi_next.activity:
            log.info('activity end process %s' % self.instance.process.title)
            # first test subflow
            lwi = WorkItem.objects.filter(activity__subflow=self.instance.process,
                                          status=WorkItem.STATUS_BLOCKED,
                                          instance=self.instance)
            if lwi.count() > 0:
                log.info('parent process for subflow %s' % self.instance.process.title)
                workitem0 = lwi[0]
                workitem0.instance.process = workitem0.activity.process
                workitem0.instance.save()
                log.info('process change for instance %s' % workitem0.instance.title)
                workitem0.status = WorkItem.STATUS_CONCLUDED
                workitem0.save()
                wi_next = workitem0.forward(request, subflow_workitem=self)
            else:
                self.instance.set_status(WorkItem.STATUS_CONCLUDED)
                # Signalize instance object associated with workflow completed
                try:
                    self.instance.wfobject().workflow_completed(self)
                except Exception as v:
                    pass

        return self if wi_next is None else wi_next

    def start_subflow(self, request):  # , actor=None
        """
        starts subflow and blocks passed in workitem
        """
        # if not actor:
        #     actor = self.user
        subflow_begin_activity = self.activity.subflow.begin
        instance = self.instance
        instance.process = self.activity.subflow
        instance.save()
        self.status = WorkItem.STATUS_BLOCKED
        self.blocked = True
        self.save()

        sub_workitem = self._forward_workitem_to_activity(request, subflow_begin_activity)
        return sub_workitem

    def check_workitem(self, user, status=(STATUS_INACTIVE, STATUS_PENDING)):
        """
        helper goal to determine whether process is:
            - enabled, etc..

        """
        if isinstance(status, str):
            status = (status,)

        if not self.activity.process.enabled:
            error = 'Processo %s desabilitado.' % self.activity.process.title
            log.error('workitem.check_workitem: %s' % error)
            raise Exception(error)

        if not self.check_user(user):
            error = 'user %s cannot take workitem %d.' % (user.username, self.pk)
            log.error('workitem.check_workitem: %s' % error)
            self.fall_out()
            raise Exception(error)

        if self.status not in status:
            error = 'workitem %d has not a correct status (%s/%s).' % (
                self.pk, self.status, str(status))
            log.error('workitem.check_workitem: %s' % error)
            raise InvalidWorkflowStatus(self, error)
        return

    def get_destinations(self, timeout_forwarding=False):
        # get_destinations(workitem, path=None, timeout_forwarding=False):
        """
        Return list of destination activities that meet the conditions of each transition

        @type timeout_forwarding: bool
        @param timeout_forwarding: a workitem with a time-delay??
        @rtype: [Activity]
        @return: list of destination activities.
        """
        transitions = Transition.objects.filter(input=self.activity)
        if timeout_forwarding:
            transitions = transitions.filter(condition__contains='workitem.timeout')
        destinations = []
        for t in transitions:
            if self.eval_transition_condition(t):
                destinations.append(t.output)
        return destinations

    def eval_transition_condition(self, transition):
        """
        evaluate the condition of a transition
        """
        instance = self.instance
        log.debug('eval_transition_condition precondition %s - %s',
                  instance.condition, transition.precondition)
        # obj pode ser usado tanto em precondition como em condition
        # obj não é usado explicitamente nessa rotina, porém pode ser usado na avaliação de precondition: obj.is_ok()
        obj = instance.wfobject()
        # self.instance.content_object.ultimo_andamento.status ==
        # self.instance.content_object.ultimo_andamento.STATUS_ANDAMENTO_CONCLUDED
        if transition.precondition:
            # precondition obrigatoriamente é uma função ou método, n
            try:
                result = eval(transition.precondition)
                # boolean expr
                if isinstance(result, bool) and result:
                    log.debug('eval_transition_condition precondition boolean %s', str(result))
                # TODO: É instance.precondition ou transaction.precondiction??? Original é instance, porém não tem esse campo em Workitem, mas em transition
                # elif isinstance(result, str) and instance.precondition == result:
                elif isinstance(result, str) and transition.precondition == result:
                    # TODO: É instance.precondition ou transaction.precondiction??? Original é instance, porém não tem esse campo em Workitem, mas em transition
                    # log.debug('eval_transition_condition precondition cmp instance.precondition %s',
                    #           str(instance.precondition == result))
                    log.debug('eval_transition_condition precondition cmp transition.precondition %s',
                              str(transition.precondition == result))
                else:
                    raise Exception('Configuração da precondition está incorreta')
            except Exception as v:
                log.debug('eval_transition_condition precondition [%s]: %s', transition.precondition, v)
                return False

        if not transition.condition:
            return True

        log.debug('eval_transition_condition %s - %s', transition.condition, instance.condition)
        try:
            # self.instance.content_object.ultimo_andamento.status ==
            # self.instance.content_object.ultimo_andamento.STATUS_ANDAMENTO_CONCLUDED
            result = eval(transition.condition)
            # boolean expr
            if isinstance(result, bool):
                log.debug('eval_transition_condition boolean %s', str(result))
                return result
            if isinstance(result, str):
                log.debug('eval_transition_condition cmp instance.condition %s', str(instance.condition == result))
                return instance.condition == result
        except Exception as v:
            log.debug('eval_transition_condition [%s]: %s', transition.condition, v)
            return instance.condition == transition.condition

        return False

    def exec_push_application(self):
        """
        Execute push application in workitem
        """
        if not self.activity.process.enabled:
            raise Exception('Processo %s desabilitado.' % self.activity.process.title)
        params = self.activity.pushapp_param
        try:
            if params:
                kwargs = eval(params)
            else:
                kwargs = {}
            result = self.activity.push_application.execute(self, **kwargs)
        except Exception as v:
            log.error('exec_push_application %s', v)
            result = None
            self.fall_out()
        return result

    def exec_auto_application(self, request):
        """
        creates a test auto application for activities that don't yet have applications
        @rtype: bool
        """
        try:
            if not self.activity.process.enabled:
                raise Exception('Processo %s desabilitado.' % self.activity.process.title)
            # no application: default auto app
            if not self.activity.application:
                return self.default_auto_app()

            func, args, kwargs = resolve(self.activity.application.get_app_url())
            params = self.activity.app_param
            # params values defined in activity override those defined in urls.py
            if params:
                params = eval('{' + params.lstrip('{').rstrip('}') + '}')
                kwargs.update(params)
            func(request, workitem=self, **kwargs)
            return True
        except Exception as v:
            log.error('execution wi %s:%s', self, v)
        return False

    def default_auto_app(self):
        """
        retrieves wfobject, logs info to it saves

        @rtype: bool
        @return: always returns True
        """
        obj = self.instance.wfobject()
        if hasattr(obj, 'history'):
            obj.history += '\n>>> execute auto activity: [%s]' % self.activity.title
            obj.save()
        return True

    def check_user(self, user):
        """returns True if authorized, False if not.

        For dummy activities, returns always True
        """
        if self.activity.kind == 'dummy':
            return True

        if user and self.user and self.user != user:
            return False
        ugroups = user.groups.all()
        agroups = self.activity.roles.all()
        authorized = False
        if agroups and len(agroups) > 0:
            for g in ugroups:
                if g in agroups:
                    authorized = True
                    break
        else:
            authorized = True
        return authorized

    def set_user(self, user, commit=True, fall_out=True):
        """affect user if he has a role authorized for activity.

        return True if authorized, False if not (workitem then falls out)
        """
        if self.check_user(user):
            self.user = user
            if commit:
                self.save()
            return True
        if fall_out:
            self.fall_out()
        return False

    def can_priority_change(self):
        """can the user change priority.

        @rtype: bool
        @return: returns True if the user can change priority

        the user must belong to a group with "workitem.can_change_priority"  permission,
        and this group's name must be the same as the process title.
        """
        if self.user.has_perm("workitem.can_change_priority"):
            lst = self.user.groups.filter(name=self.instance.process.title)
            if lst.count() == 0 or \
                    (lst[0].permissions.filter(codename='can_change_priority').count() == 0):
                return False
            return True
        return False

    def block(self):
        self.status = WorkItem.STATUS_BLOCKED
        self.save()
        Event.objects.create(name=WorkItem.STATUS_BLOCKED, workitem=self)

    def fall_out(self):
        self.status = WorkItem.STATUS_FALLOUT
        self.save()
        roles = Group.objects.filter(name='workflow-admin')
        task = WorkItemManager.notify_if_needed(workitems=[self, ], roles=roles,
                                                subject='Workflow Error: fall out workitem %s' % self,
                                                template='goflow/mail-fall-out')
        Event.objects.create(name=WorkItem.STATUS_FALLOUT, workitem=self, external_task=task)

    def timeout(self, delay, unit='days'):
        """
        return True if timeout reached
          delay:    nb units
          unit: 'weeks' | 'days' | 'hours' ... (see timedelta)
        """
        tdelta = eval('timedelta(' + unit + '=' + delay + ')')
        now = timezone.now()
        return now > (self.date + tdelta)

    def events_list(self):
        """provide html link to events for a workitem in admin change list.
        @rtype: string
        @return: html href link "../event/?workitem__id__exact=[self.id]&ot=asc&o=0"
        """
        nbevt = self.events.count()
        return mark_safe('<a href=../event/?workitem__id__exact=%d&ot=asc&o=0>%d item(s)</a>' % (self.pk, nbevt))

    @property
    def html_action(self):
        if self.status == WorkItem.STATUS_INACTIVE:
            label = 'activate'
        elif self.status == WorkItem.STATUS_PENDING:
            label = 'complete'
        elif self.status == WorkItem.STATUS_CONCLUDED:
            label = 'completed'
        else:
            label = 'action'
        return '<a href=%s/%d/>%s</a>' % (label, self.id, label)

    @property
    def html_to_approve_link(self):
        """
        Retorna caminho para a ação do workflow em função do status

        No momento ignora o status e força 'workflow'
        """
        # if self.status == WorkItem.STATUS_INACTIVE:
        #     label = 'activate'
        # elif self.status == WorkItem.STATUS_PENDING:
        #     label = 'complete'
        # else:
        #     label = 'action'
        label = reverse('workflow_action', args=[self.id])
        return label

    def __str__(self):
        return u'%s: %s' % (self.activity.__str__(), self.instance.__str__())

    class Meta:
        permissions = (
            ("can_change_priority", "Can change priority"),
        )


class Event(models.Model):
    """Event are changes that happens on workitems.
    """
    date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    workitem = models.ForeignKey(WorkItem, related_name='events', on_delete=models.CASCADE)
    # external_task = models.CharField(max_length=50, verbose_name='Celery Task', null=True, blank=True)
    external_task = models.UUIDField(verbose_name='Celery Task', default=None, editable=False, null=True, blank=True)

    def __str__(self):
        return self.name
