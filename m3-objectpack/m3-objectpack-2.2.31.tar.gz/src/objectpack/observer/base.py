# coding: utf-8
from __future__ import absolute_import

import inspect
import logging
import re
import sys

import six

from m3 import actions as m3_actions
from m3_django_compat import get_request_params

from . import tools


ACTION_NAME_ATTR = '_observing_name'


def _warn(msg, level=3):
    """
    Костыль для вывода предупреждений в лог
    """
    frame = sys._getframe(level)
    fmt = '%%s (%s:%s)' % (frame.f_globals['__name__'], frame.f_lineno)
    logging.warn(fmt % msg)


# =============================================================================
# ControllerMixin
# =============================================================================
class ObservableMixin(object):
    """
    Наблюдатель за вызовом actions и кода в точках их (actions) расшрения
    """

    def __init__(self, observer, *args, **kwargs):
        super(ObservableMixin, self).__init__(*args, **kwargs)
        self._observer = observer
        self._already_registered = set()

    def _invoke(self, request, action, stack):
        """
        Вызов action под наблюдением
        """
        self._observer.configure()

        stack = stack[:]
        self._observer._prepare_for_listening(action, request, stack)

        # обработка контроллером
        with action._catcher as catcher:
            return super(ObservableMixin, self)._invoke(request, action, stack)
        return catcher.result

    def append_pack(self, pack):
        """
        Добавление ActionPack`а с регистрацией его action`ов в ObserVer`е
        """
        self._observer._populate_pack(
            super(ObservableMixin, self).append_pack(pack)
        )


# =============================================================================
# ObservableController
# =============================================================================
class ObservableController(ObservableMixin, m3_actions.ActionController):
    """
    Контроллер, поддерживающий механизм подписки через Observer
    """
    class VerboseDeclarativeContext(m3_actions.DeclarativeActionContext):

        __internal_attrs = ['m3_window_id']

        def __init__(self, debug, **kwargs):
            m3_actions.DeclarativeActionContext.__init__(self, **kwargs)
            self.__debug = debug
            self.__declared = []

        def build(self, request, rules):
            self.__declared = list(rules.keys()) + self.__internal_attrs
            try:
                m3_actions.DeclarativeActionContext.build(self, request, rules)
            except m3_actions.CriticalContextBuildingError as e:
                if self.__debug:
                    raise
                else:
                    _warn('%r, url="%s"' % (e, request.path_info))
            for k, v in six.iteritems(get_request_params(request)):
                if not hasattr(self, k):
                    setattr(self, k, v)

        def __getattr__(self, attr, default=(((),),)):
            if not attr.startswith('__'):
                if attr not in self.__declared:
                    _warn('Attribute "%s" not declared!' % attr)
            try:
                return self.__dict__[attr]
            except KeyError:
                if default == (((),),):
                    raise AttributeError(
                        "'%s' object has no attribute '%s'" % (
                            self.__class__.__name__, attr
                        ))
                return default

    def build_context(self, request, rules):
        """
        Выполняет построение контекста вызова операции ActionContext
        на основе переданного request
        """
        if isinstance(rules, dict):
            from django.conf import settings
            return self.VerboseDeclarativeContext(debug=settings.DEBUG)
        else:
            return m3_actions.ActionContext()


# =============================================================================
# Observer
# =============================================================================
class Observer(object):
    """
    Реестр слушателей, реализующий подписку последних на действия в actions
    """
    # уровни детализации отладочного логировния
    LOG_NONE, LOG_WARNINGS, LOG_CALLS, LOG_MORE = 0, 1, 2, 3

    class _BeforeAfterPack:
        """
        Обертка для списка слушателей, реализующая вызов before/after
        в соответствии с приоритетом, определяемым порякрм слушателей
        """

        def __init__(self, action, listeners, logger):
            self._listeners = listeners
            self._action = action
            self._logger = logger

        @staticmethod
        def lazy_chain(methods, *args):
            for m in methods:
                result = m(*args)
                if result:
                    return result

        def _execute(self, verb, *args):
            # реакция слушателей на действие @verb=(before|after)
            for listener in self._listeners:
                # слушатель должен иметь метод с именем из verb
                method = getattr(listener, verb, None)
                if method:
                    # слушатель инстанцируется каждый раз
                    listener = listener()
                    # логирование
                    self._logger(
                        'Listener call:\n\t'
                        'Action\t %r\n\tListener %r\n\tVerb\t "%s"' %
                        (self._action, listener, verb))
                    # инжекция action в слушателя
                    listener.action = self._action
                    # вызывается метод слушателя для
                    # нового экземпляра слушателя
                    result = method(listener, *args)
                    if result:
                        return result

        def pre_run(self, *args):
            return self._execute('before', *args)

        def post_run(self, *args):
            return self._execute('after', *args)

    def __init__(self, logger=lambda msg: None, verbose_level=LOG_WARNINGS):
        """
        Создание наблюдателя.
        @logger - метод логирования: callable-объект,
            вызываемый для каждого сообщения (параметр - текст сообщения)
        @verbose_level - уровень подробности логирования:
            одна из констант Observer.LOG_xxx
        """
        self._logger = logger
        self._verbose_level = verbose_level

        self._registered_listeners = []
        self._action_listeners = {}
        self._actions = {}

        self._model_register = {}
        self._pack_instances_by_name = {}

        self._is_configured = False

    def get(self, model_name):
        """
        Поиск экземпляра ActionPack для модели по имени её класса.
        Поиск производится среди зарегистрированных Pack`ов, которые являются
        основными для своих моделей (и привязаны к модели)
        """
        return self._model_register.get(model_name)

    def get_pack_instance(self, pack):
        """
        Возвращает экземпляр зарегистрированного ActionPack.
        @pack может быть:
        - классом
        - строкой с именем класса в формате "package/ClassName"
        """
        if inspect.isclass(pack):
            pack = tools._name_class(pack)
        return self._pack_instances_by_name.get(pack)

    def _log(self, level, message):
        """
        Логирование действий с проверкой уровня подробности
        """
        if self._verbose_level >= level:
            self._logger(message)

    def _name_action(self, action, pack_name=None):
        """
        Получение / генерация полного имени для @action
        """
        name = getattr(action, ACTION_NAME_ATTR, None)
        if not name:
            name = tools.name_action(action, pack_name)
            # название подписки проставляется в экземпляр action
            action._observing_name = name

            self._log(
                self.LOG_MORE,
                'Name gererated:\n\tAction\t %r\n\tname\t "%s"'
                % (action, name))

        return name

    def configure(self, force=False):
        """
        Построение дерева сопоставления экшнов со слушателями
        Если observer был сконфигурирован ранее и в него ничего не добавили,
        то построение выполнится, только если передан аргумент `force=True`

        :param bool force: Форсировать конфигурирование
        """
        # конфижим листенеры только понеобходимости
        if self._is_configured and not force:
            return

        self._action_listeners = {}
        # слушатели сортируются по приоритету
        listeners = [
            l[1] for l in
            sorted(self._registered_listeners, key=lambda x: x[0])
        ]
        # зарегистрированные actions получают подписчиков
        for name in self._actions:
            action_listeners = []
            for is_listen, listener in listeners:
                if is_listen(name):
                    action_listeners.append(listener)
                    self._log(
                        self.LOG_MORE,
                        'Action linked:\n\tshort_name\t "%s"'
                        '\n\tListener\t %r' % (name, listener))
            self._action_listeners[name] = action_listeners

        self._is_configured = True

    def _populate_pack(self, pack):
        """
        Подписка зарегистрированных слушателей на pack.actions
        """
        # каждый отдельный Pack должен регистрироваться ровно один раз
        # уникльность Pack определяется следующим ключом
        pack_name = tools._name_class(pack.__class__)
        if pack_name in self._pack_instances_by_name:
            # попытка перерегистрации отмечается предупреждением
            raise RuntimeError(
                'WARNING! Pack reregistration blocked!:\n\tPack: %s'
                % pack_name
            )
        else:
            # ActionPack запоминается, как уже зарегистрированный
            self._pack_instances_by_name[pack_name] = pack
            self._log(
                self.LOG_MORE,
                'Pack reregistered:\n\tPack: %s'
                % pack_name)

        # регистрация ActionPack, как основного для модели
        model = getattr(pack, 'model', getattr(pack, 'tree_model', None))
        if model and getattr(pack, '_is_primary_for_model', True):
            model_name = model.__name__
            try:
                # если для модели уже зарегистрирован ActionPack
                # возбуждается исключение
                raise AssertionError(
                    "For model %s already registered primary pack: %r"
                    % (model_name, self._model_register[model_name]))
            except KeyError:
                # модель ещё не регистрировалась - регистрируется
                self._model_register[model_name] = pack

        # в Pack инжектируется функция получения Pack`а
        # для указанной по имени модели
        pack._get_model_pack = self.get

        for action in pack.actions:
            name = self._name_action(action, pack_name)
            # возбуждение исключения при коллизии short_names
            if name in self._actions:
                raise RuntimeError(
                    'Name="%s" can not be registered for action %r,\n'
                    'because this name registered for %r!'
                    % (name, action, self._actions[name]))
            self._actions[name] = action

        for subpack in pack.subpacks:
            self._populate_pack(subpack)

        self._is_configured = False

    def subscribe(self, listener):
        """
        Декоратор, регистрирующий слушателя @listener в реестре слушателей
        """
        priority = getattr(listener, 'priority', 0) or 0

        # matcher`ы по списку рег.выр. в параметре "from" слушателя
        matchers = [
            re.compile(p).match
            for p in getattr(listener, 'listen', [])
        ]
        if matchers:
            def is_listen(name):
                return any(m(name) for m in matchers)
        else:
            # если from не указан - слушатель слушает всех
            def is_listen(name):
                return True

        self._registered_listeners.append(
            (priority, (is_listen, listener))
        )
        self._log(
            self.LOG_MORE,
            'Listener registered:\n\tListener %r' % listener)

        self._is_configured = False

        return listener

    def _configure_action(self, action, request, listeners):
        """
        Конфигурирует @action, инжектируя в него методы handle и handler_for,
        взаимрдействующие со слушателями @listeners
        """
        def log_call(listener, verb):
            self._log(
                self.LOG_CALLS,
                'Listener call:\n\t'
                'Action\t %r\n\tListener %r\n\tVerb\t "%s"' %
                (action, listener, verb)
            )

        def handle(verb, arg):
            """
            Обработка данных @arg подписанными слушателями, которые имеют
            обработчик @verb
            """
            for listener in listeners:
                handler = getattr(listener, verb, None)
                if handler:
                    log_call(listener, verb)
                    # слушатель инстанцируется каждый раз
                    listener = listener()
                    # инжекция action/request в слушателя
                    listener.action = action
                    listener.request = request
                    # вызывается метод слушателя для
                    # нового экземпляра слушателя
                    arg = handler(listener, arg)
            return arg

        def handler_for(verb):
            """
            Декоратор для обертки пользовательской функции
            обработчиком (с именем @verb) на стороне слушателей
            """
            def wrapper(fn):
                def inner(*args, **kwargs):
                    return handle(verb, fn(*args, **kwargs))
            return wrapper

        class ExceptionHandlingCM(object):
            """
            ContextManager, передающий исключения на обработку
            в listeners. Если ни один из слушетелей не вернёт
            True, исключение считается неотловленным
            """
            def __init__(self):
                self.result = None

            def __enter__(self):
                return self

            def __exit__(self, *args):
                for listener in listeners:
                    handler = getattr(listener, 'catch', None)
                    if handler:
                        log_call(listener, 'catch')
                        listener = listener()
                        listener.action = action
                        listener.request = request
                        # обработчик должен вернуть Response
                        # в случае успешной обработки исключения
                        result = handler(listener, args)
                        if result:
                            self.result = result
                            return True

        action._catcher = ExceptionHandlingCM()
        action.handle = handle
        action.handler_for = handler_for

    def _prepare_for_listening(self, action, request, stack):
        """
        Подготовка action к прослушиванию (инжекция методов)
        """
        listeners = self._action_listeners.get(self._name_action(action), [])

        # в action инжектируются методы для работы подписки,
        # причем инжектирование производится и в случае,
        # когда подписчиков нет - для консистентности
        self._configure_action(action, request, listeners)

        # если подписчики есть, в стек паков добавляется "пак",
        # реализующий подписку на before/after
        if listeners:
            stack.insert(0, self._BeforeAfterPack(
                action, listeners,
                # инжекция логирования
                logger=lambda msg: self._log(self.LOG_CALLS, msg)
            ))
