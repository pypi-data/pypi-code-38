import json
import logging
import traceback
from collections import OrderedDict

from django.conf import settings

from ievv_opensource.utils.singleton import Singleton


class ActionResult(object):
    def __init__(self, actionclass):
        self.actionclass = actionclass
        self.failed = False
        self.success_output_data = None
        self.exception_traceback = None
        self.exception = None

    def set_exception(self, exception, exception_traceback):
        self.failed = True
        self.exception = exception
        self.exception_traceback = exception_traceback

    def set_success_output_data(self, success_output_data):
        self.success_output_data = success_output_data

    def get_error_data(self):
        if isinstance(self.exception, ActionError):
            return self.exception.error_data_dict
        else:
            return str(self.exception)

    def get_exception_traceback(self):
        return self.exception_traceback

    def get_errordata(self):
        if self.exception:
            return {
                'data': self.get_error_data(),
                'traceback': self.get_exception_traceback()
            }
        else:
            return None

    def to_dict(self):
        return {
            'action_name': self.actionclass.get_name(),
            'failed': self.failed,
            'errordata': self.get_errordata(),
            'success_output_data': self.success_output_data
        }


class ActionGroupResult(object):
    def __init__(self, actiongroup):
        self.actiongroup = actiongroup
        self._actionresults = OrderedDict()

    def __getitem__(self, actiongroup_name):
        return self._actionresults[actiongroup_name]

    def __iter__(self):
        return self._actionresults.values()

    @property
    def failed(self):
        for actionresult in self._actionresults.values():
            if actionresult.failed:
                return True
        return False

    def add_actionresult(self, actionresult):
        self._actionresults[actionresult.actionclass.get_name()] = actionresult

    def to_dict(self):
        resultlist = []
        for actionresult in self._actionresults.values():
            resultlist.append(actionresult.to_dict())
        return {
            'actiongroup_name': self.actiongroup.name,
            'results': resultlist
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


class ActionGroupSynchronousExecutionError(Exception):
    def __init__(self, actiongroupresult):
        self.actiongroupresult = actiongroupresult

    def __str__(self):
        return json.dumps(self.actiongroupresult.to_dict(), indent=4)


class ActionError(Exception):
    def __init__(self, error_data_dict):
        self.error_data_dict = error_data_dict

    def __str__(self):
        return json.dumps(self.error_data_dict, indent=4)

    def __repr__(self):
        return str(self)


def action_factory(baseclass, name):
    """
    Factory for creating :class:`.Action` classes. This is simply
    a thin wrapper around ``type`` to dynamically create a subclass
    of the given ``baseclass`` with a different name.

    There are two use cases for using this:

    - Give re-usable action classes a better name.
    - Use the same :class:`.Action` subclass multiple times in the same
      :class:`.ActionGroup`.

    Both of these cases can also be solved with subclasses, and that
    is normally a better solution.

    Args:
        baseclass: The class to create a subclass of.
        name: The name of the subclass.
    """
    return type(name, (baseclass,), {})


class Action(object):
    """
    An action is the subclass for code that can be executed as
    part of an :class:`.ActionGroup`.

    You create a subclass of this class, and override :meth:`.exectute`
    to implement an action, and you add your subclass to an
    :class:`.ActionGroup` to use your action class.
    """
    @classmethod
    def run(cls, **kwargs):
        """
        Run the action - used internally.

        Args:
            kwargs: Kwargs for the action.
            executed_by_celery: Must be ``True`` if the action is executed by a celery task.
                This is required to configure the correct logger.
        """
        action = cls(**kwargs)
        action.execute()

    @classmethod
    def get_name(cls):
        """
        Get the name of this action.
        """
        return '{}.{}'.format(
            cls.__module__,
            cls.__name__)

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        # self.logger = kwargs['logger']

    @property
    def logger(self):
        """
        Get the logger for this action.
        """
        logname = self.__class__.get_name()
        return logging.getLogger(logname)

    @property
    def executed_by_celery(self):
        return self.kwargs.get('executed_by_celery', False)

    @property
    def context_object(self):
        return self.kwargs['context_object']

    @property
    def started_by(self):
        return self.kwargs['started_by']

    def execute(self):
        """
        Execute the action. Must be overridden in subclasses.
        """
        raise NotImplementedError()


class ActionGroupExecutionInfo(object):
    """
    Return value from :meth:`.ActionGroup.run`, with information about
    how the ActionGroup was executed.

    .. attribute:: actiongroup
        The :class:`.ActionGroup` object that was executed.

    .. attribute:: mode
        The mode the ActionGroup was executed with.

    .. attribute:: route_to_alias
        The route_to_alias that was used to route/prioritize the execution of
        the ActionGroup.
    """
    def __init__(self, actiongroup, mode, route_to_alias,
                 actiongroupresult=None, batchoperation=None):
        self.actiongroup = actiongroup
        self.mode = mode
        self.route_to_alias = route_to_alias
        self._actiongroupresult = actiongroupresult
        self._batchoperation = batchoperation

    @property
    def is_asynchronous(self):
        """
        Property that returns ``True`` if the ActionGroup was executed
        asynchronously.
        """
        return self.mode == ActionGroup.MODE_ASYNCHRONOUS

    @property
    def actiongroupresult(self):
        """
        Property for getting the :class:`.ActionGroupResult` if the
        ActionGroup was executed in synchronous mode.

        Raises:
            AttributeError: If ``mode`` is :obj:`.ActionGroup.MODE_ASYNCHRONOUS`.
        """
        if self.is_asynchronous:
            raise AttributeError(
                'Can not use ActionGroupExecutionInfo.actiongroupresult when execution mode '
                'is asynchronous. In asynchronous mode, this is stored in a BatchOperation object '
                'when the asynchronous operation is finished. You can get BatchOperation object '
                'using the batchoperation property.'
            )
        else:
            return self._actiongroupresult

    @property
    def batchoperation(self):
        """
        Property for getting the :class:`ievv_opensource.ievv_batchframework.models.BatchOperation`
        object that was created if the ActionGroup was executed in asynchronous mode.

        Raises:
            AttributeError: If ``mode`` is :obj:`.ActionGroup.MODE_ASYNCHRONOUS`.
        """
        if self.is_asynchronous:
            return self._batchoperation
        else:
            raise AttributeError(
                'Can not use ActionGroupExecutionInfo.batchoperation when execution mode '
                'is synchronous. In synchronous mode, you can use the actiongroupresult '
                'property to access the results.'
            )

    def __str__(self):
        common_str = '{}.{}(mode={!r}, route_to_alias={!r})'.format(
            self.actiongroup.__class__.__module__,
            self.actiongroup.__class__.__name__,
            self.mode, self.route_to_alias)
        if self.is_asynchronous:
            return '{} - BatchOperation({})'.format(common_str, self.batchoperation)
        else:
            return '{} - ActionGroupResult({})'.format(common_str, self.actiongroupresult)


class ActionGroup(object):
    """
    An ActionGroup is a list of :class:`actions <.Action>` that can be
    executed both synchronously and asynchronously.
    """

    #: Constant for asynchronous (background/Celery) mode of execution.
    MODE_ASYNCHRONOUS = 'asynchronous'

    #: Constant for synchronous (blocking) mode of execution.
    MODE_SYNCHRONOUS = 'synchronous'

    def __init__(self, name, actions=None, mode=None, route_to_alias=None):
        """
        Args:
            name: The name of the ActionGroup.
            actions: A list of actions.
            mode: The default mode of the ActionGroup.
                Defaults to :obj:`~.ActionGroup.MODE_ASYNCHRONOUS`.
                You will often want to determine this from the input
                (I.E.: Use asynchronous if sending more than 500 newsletters),
                and this can be done by extending this class and overriding
                :meth:`.get_mode`.
            route_to_alias: Defines where to route this ActionGroup when
                is is executed in asynchronous mode. Defaults to
                :obj:`.Registry.ROUTE_TO_ALIAS_DEFAULT`.
                You can determine the route dynamically each time the ActionGroup
                is executed by overriding :meth:`.get_route_to_alias`.
        """
        self.name = name
        self.mode = mode or self.MODE_ASYNCHRONOUS
        # self.route_to_alias = route_to_alias or Registry.ROUTE_TO_ALIAS_DEFAULT
        self.route_to_alias = route_to_alias or Registry.ROUTE_TO_TASK_ALIAS_DEFAULT
        self.actions = OrderedDict()
        self.registry = None  # Set when the ActionGroup is added to the Registry
        if actions:
            self.add_actions(actions=actions)

    def add_action(self, action):
        """
        Add a action.

        Args:
            action: A subclass of :class:`.Action` (not an object, but a class).
        """
        name = action.get_name()
        if name in self.actions:
            raise ValueError(
                'Duplicate action class in one ActionGroup: {name}. '
                'You can not register more than one action of the same class in the same '
                'ActionGroup. Create multiple subclasses of {name}, or use batchregistry.action_factory: '
                'actions=[batchregistry.action_factory({classname}, name="FirstAction"), '
                'batchregistry.action_factory({classname}, name="SecondAction")].'.format(
                    name=name, classname=action.__name__))
        self.actions[name] = action

    def add_actions(self, actions):
        """
        Add actions.

        Args:
            actions: A list of :class:`.Action` subclasses (classes not actions).
        """
        for action in actions:
            self.add_action(action=action)

    def get_mode(self, **kwargs):
        """
        Get the mode to run the ActionGroup in.
        Must return one of :obj:`~.ActionGroup.MODE_ASYNCHRONOUS` or :obj:`~.ActionGroup.MODE_SYNCHRONOUS`.

        The use-case for overriding this method is optimization. Lets say
        you have to re-index your blogposts in a search engine each time they
        are updated. If you update just a few blogpost, you may want to do
        that in synchronous mode, but if you update 500 blogposts, you will
        probably want to re-index in asynchronous mode (I.E. in Celery).

        Args:
            kwargs: The ``kwargs`` the user provided to :meth:`.run`.
        """
        return self.mode

    def get_route_to_alias(self, **kwargs):
        """
        Define where to route this ActionGroup when is is executed in asynchronous mode.

        This is the method you want to override to handle priority of your
        asynchronously executed ActionGroups.

        Lets say you have a huge blog, with lots of
        traffic. After updating a blogpost, you need to do some heavy postprocessing
        (image optimization, video transcoding, etc.). If you update a newly posted blogpost
        this postprocessing should be placed in a high-priority queue, and if you update an old
        blogpost, this postprocessing should be placed in a low-priority queue. To achieve this,
        you simply need to create a subclass of ActionGroup, and override this method
        to return :obj:`.Registry.ROUTE_TO_ALIAS_HIGHPRIORITY` for recently created blogpost, and
        :obj:`.Registry.ROUTE_TO_ALIAS_DEFAULT` for old blogposts.

        Args:
            kwargs: The ``kwargs`` the user provided to :meth:`.run_asynchronous`.

        Returns:
            str: One of the route-to aliases added to the :class:`.Registry`
            using :meth:`.Registry.add_route_to_alias`. This will always include
            :obj:`.Registry.ROUTE_TO_ALIAS_DEFAULT` and :obj:`.Registry.ROUTE_TO_ALIAS_HIGHPRIORITY`.
        """
        return self.route_to_alias

    def run_blocking(self, **kwargs):
        # This method is for internal use only.
        actiongroupresult = ActionGroupResult(actiongroup=self)
        for actionclass in self.actions.values():
            actionresult = ActionResult(actionclass=actionclass)
            try:
                success_output_data = actionclass.run(**kwargs)
            except Exception as exception:
                exception_traceback = traceback.format_exc()
                actionresult.set_exception(
                    exception=exception,
                    exception_traceback=exception_traceback)
            else:
                actionresult.set_success_output_data(
                    success_output_data=success_output_data)
            actiongroupresult.add_actionresult(actionresult=actionresult)
        return actiongroupresult

    def run_synchronous(self, **kwargs):
        """
        Run the ActionGroup in blocking/synchronous mode.

        Args:
            kwargs: Kwargs for :class:`.Action`.
        """
        actiongroupresult = self.run_blocking(**kwargs)
        if actiongroupresult.failed:
            raise ActionGroupSynchronousExecutionError(actiongroupresult=actiongroupresult)
        else:
            return ActionGroupExecutionInfo(
                actiongroup=self,
                mode=self.MODE_SYNCHRONOUS,
                route_to_alias=None,
                actiongroupresult=actiongroupresult
            )

    def get_batchoperation_options(self, **kwargs):
        """
        You can override this if you create a re-usable ActionGroup subclass that
        sets options for the :class:`ievv_opensource.ievv_batchframework.models.BatchOperation`
        based on ``kwargs``.

        Called by :meth:`.run_asynchronous` to get the kwargs for
        :meth:`ievv_opensource.ievv_batchframework.models.BatchOperationManager.create_asynchronous`.

        If you override this, you should normally call ``super()``, and update the kwargs
        returned by super.

        Args:
            kwargs: The ``kwargs`` the user provided to :meth:`.run_asynchronous`.

        Returns:
            dict: Kwargs for
            :meth:`ievv_opensource.ievv_batchframework.models.BatchOperationManager.create_asynchronous`
        """
        options = {
            'operationtype': self.name,
            'context_object': kwargs.get('context_object', None),
            'started_by': kwargs.get('started_by', None),
        }
        return options

    def create_batchoperation(self, **kwargs):
        """
        Used by :meth:`.run_asynchronous` to create the
        :class:`ievv_opensource.ievv_batchframework.models.BatchOperation` object.

        You normally do not need to override this - override :meth:`.get_batchoperation_options`
        instead.

        .. warning:: Overriding this may lead to breaking code if the inner workings of this framework
            is changed/optimized in the future.

        Args:
            kwargs: See :meth:`.run_asynchronous`.

        Returns:
            BatchOperation: The created :class:`ievv_opensource.ievv_batchframework.models.BatchOperation`.
        """
        from ievv_opensource.ievv_batchframework.models import BatchOperation
        batchoperation_options = self.get_batchoperation_options(**kwargs)
        batchoperation = BatchOperation.objects.create_asynchronous(**batchoperation_options)
        return batchoperation

    def run_asynchronous(self, **kwargs):
        """
        Args:
            kwargs: Kwargs for :class:`.Action`.
        """
        batchoperation = self.create_batchoperation(**kwargs)
        full_kwargs = {
            'actiongroup_name': self.name,
            'batchoperation_id': batchoperation.id
        }
        full_kwargs.update(kwargs)

        # Remove the kwargs that is stored in the batchoperation
        full_kwargs.pop('context_object', None)
        full_kwargs.pop('started_by', None)

        route_to_alias = self.get_route_to_alias(**kwargs)
        self.registry.queue_to_task_map[route_to_alias].delay(
            **full_kwargs
        )
        return ActionGroupExecutionInfo(
            actiongroup=self,
            mode=self.MODE_ASYNCHRONOUS,
            route_to_alias=route_to_alias,
            batchoperation=batchoperation)

    def run(self, **kwargs):
        """
        Runs one of :meth:`.run_asynchronous` and :meth:`.run_synchronous`. The method to
        run is determined by the return-value of :meth:`.get_mode`:

        - If :meth:`.get_mode` returns :obj:`~.ActionGroup.MODE_ASYNCHRONOUS`, :meth:`.run_asynchronous`
          is called.
        - If :meth:`.get_mode` returns :obj:`~.ActionGroup.MODE_SYNCHRONOUS`, :meth:`.run_synchronous`
          is called.

        Args:
            context_object: context_object for :class:`ievv_opensource.ievv_batchframework.models.BatchOperation`.
            started_by: started_by for :class:`ievv_opensource.ievv_batchframework.models.BatchOperation`.
            **kwargs: Kwargs for :class:`.Action`. Forwarded to :meth:`.run_asynchronous` and
                :meth:`.run_synchronous`.
        """
        if getattr(settings, 'IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS', False):
            mode = self.MODE_SYNCHRONOUS
        else:
            mode = self.get_mode(**kwargs)
        if mode == self.MODE_ASYNCHRONOUS:
            return self.run_asynchronous(**kwargs)
        else:
            return self.run_synchronous(**kwargs)


class Registry(Singleton):
    """
    The registry of :class:`.ActionGroup` objects.
    """
    ROUTE_TO_TASK_ALIAS_DEFAULT = 'default'
    ROUTE_TO_TASK_ALIAS_HIGHPRIORITY = 'highpriority'

    def __init__(self):
        self.actiongroups = OrderedDict()
        self.queue_to_task_map = {}
        self.__add_default_route_to_aliases()
        super(Registry, self).__init__()

    def __add_default_route_to_aliases(self):
        from ievv_opensource.ievv_batchframework.rq_tasks import default, highpriority
        self.add_route_to_alias(
            route_to_alias=self.ROUTE_TO_TASK_ALIAS_DEFAULT,
            task_callable=default,
        )
        self.add_route_to_alias(
            route_to_alias=self.ROUTE_TO_TASK_ALIAS_HIGHPRIORITY,
            task_callable=highpriority,
        )

    def add_route_to_alias(self, route_to_alias, task_callable):
        """
        Add a route-to alias.

        Args:
            route_to_alias (str): The alias.
            task_callable (func): The callable rq task.
        """
        self.queue_to_task_map[route_to_alias] = task_callable


    def add_actiongroup(self, actiongroup):
        """
        Add an :class:`.ActionGroup` to the registry.

        Args:
            actiongroup: The :class:`.ActionGroup` object to add.
        """
        actiongroup.registry = self
        self.actiongroups[actiongroup.name] = actiongroup

    def remove_actiongroup(self, actiongroup_name):
        """
        Remove an :class:`ActionGroup` from the registry.

        Args:
            actiongroup_name: The name of the actiongroup.

        Raises:
            KeyError: If no :class:`.ActionGroup` with the provided
                ``actiongroup_name`` exists in the registry.
        """
        del self.actiongroups[actiongroup_name]

    def get_actiongroup(self, actiongroup_name):
        """
        Get an :class:`.ActionGroup` object from the registry.

        Args:
            actiongroup_name: The name of the actiongroup.

        Returns:
            ActionGroup: An :class:`.ActionGroup` object.

        Raises:
            KeyError: If no :class:`.ActionGroup` with the provided
                ``actiongroup_name`` exists in the registry.
        """
        return self.actiongroups[actiongroup_name]

    def run(self, actiongroup_name, **kwargs):
        """
        Shortcut for::

            Registry.get_instance().get_actiongroup(actiongroup_name)\
                .run(**kwargs)

        .. seealso:: :meth:`.get_actiongroup` and :meth:`.ActionGroup.run`.
        """
        return self.get_actiongroup(actiongroup_name=actiongroup_name).run(**kwargs)
