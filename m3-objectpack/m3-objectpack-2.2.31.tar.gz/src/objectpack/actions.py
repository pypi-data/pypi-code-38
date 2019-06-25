# coding: utf-8
u"""Этот модуль содержит главный класс библиотеки и набор actions для него."""
from __future__ import absolute_import

import copy
import datetime
import json
import warnings

import six

from django.core import exceptions as dj_exceptions
from django.db.models import fields as dj_fields
from django.utils.encoding import force_text
from m3 import ApplicationLogicException
from m3 import RelatedError
from m3.actions import Action
from m3.actions import ActionPack
from m3.actions import ControllerCache
from m3.actions.context import ActionContext
from m3.actions.interfaces import IMultiSelectablePack
from m3.actions.results import OperationResult
from m3.actions.results import PreJsonResult
from m3.actions.utils import apply_search_filter
from m3.actions.utils import extract_int
from m3.db import safe_delete
from m3_django_compat import atomic
from m3_django_compat import ModelOptions
from m3_django_compat import get_request_params
from m3_ext.ui.results import ExtUIScriptResult

from . import exceptions
from . import filters
from . import tools
from . import ui


# =============================================================================
# BaseAction
# =============================================================================
class BaseAction(Action):
    """
    Базовый класс для всех actions.

    Имеет автоматически-генерируемый url и
    возможность подключений точек расширения в |Observer|.
    """

    perm_code = None
    """
    Код подправа, используемый при формировании кода права экшна
    стандартным способом. Если код не указан - экшн формирует
    свой код права независимо от пака
    """

    @property
    def url(self):
        u"""
        автоматически генерируемый url
        """
        return r'/%s' % self.__class__.__name__.lower()

    @tools.cached_to('__cached_context_declaration')
    def context_declaration(self):
        """
        Делегирует декларацию контекста в пак

        :return: Правила для DeclarativeActionContext
        :rtype: dict
        """
        return self.parent.declare_context(self)

    def get_perm_code(self, subpermission=None):
        """
        Возвращает код права

        :param subpermission: Код подправа доступа
        :type subpermission: str
        :return: code - Код доступа
        :rtype: str
        """
        if self.perm_code is None:
            code = super(BaseAction, self).get_perm_code(subpermission)
        else:
            perm_code = self.perm_code + (
                ('/' + subpermission) if subpermission else ''
            )
            code = self.parent.get_perm_code(perm_code)
        return code

    @property
    @tools.cached_to('__cached_need_check_permission')
    def need_check_permission(self):
        """
        Небходимость проверки прав

        Если определен perm_code, то необходимость проверки прав
        будет зависеть от присутствия perm_code среди sub_permissions пака
        и соответствующего флага пака

        :rtype: bool
        """
        if self.perm_code is not None:
            result = self.parent.need_check_permission and (
                self.perm_code in self.parent.sub_permissions
            )
        else:
            result = False
        return result

    @staticmethod
    def handle(verb, arg):
        """
        Заглушка для точек расширения.
        При регистрации в обсервер перекрывается

        :param verb: Имя точки расширения
        :type verb: str
        :param arg: Объект для передачи в точку расширения
        :type arg: any
        :return arg: Тот же объект или любой другой
        """
        return arg


# =============================================================================
# BaseWindowAction
# =============================================================================
class BaseWindowAction(BaseAction):
    """
    Базовый Action показа окна
    """

    def create_window(self):
        """
        Метод инстанцирует окно и помещает экземпляр в атрибут self.win

        .. code::

            def create_window(self):
                self.win = EditWindow()
        """
        raise NotImplementedError()

    def set_windows_params(self):
        """
        :deprecated:
        :TODO: Выпилить, ато опечатка портит всю семантику!
        """
        warnings.warn(
            'Please, replace "set_windowS_params"->"set_window_params"!',
            category=FutureWarning)
        self.set_window_params()

    def _apply_windows_params(self):
        """
        :TODO: Выпилить, ато опечатка портит всю семантику!
        """
        warnings.warn(
            'Please, replace "_apply_windowS_params"->"_apply_window_params"!',
            category=FutureWarning)
        self._apply_window_params()

    def set_window_params(self):
        """
        Метод заполняет словарь self.win_params, который будет передан
        в окно. Этот словарь выступает как шина передачи данных
        от Actions/Packs к окну

        .. code::

            def set_window_params(self):
                self.win_params['title'] = _(u'Привет из ада')
        """
        pass

    def _apply_window_params(self):
        """
        Метод передает словарь параметров в окно.

        .. note:

            Обычно не требует перекрытия
        """
        self.win.set_params(self.win_params)

    def configure_window(self):
        """
        Точка расширения, предоставляющая доступ к настроенному
        экземпляру окна для тонкой настройки.

        .. note::

           Оставлена для особо тяжёлых случаев, когда не удаётся
           обойтись set_params

        .. code::

            def configure_window(self):
                self.win.grid.top_bar.items[8].text = _(u'Ух ты, 9 кнопок')
        """
        pass

    def run(self, request, context):
        """
        Тело Action, вызывается при обработке запроса к серверу.

        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext

        .. note::

           Обычно не требует перекрытия
        """
        new_self = copy.copy(self)
        new_self.win_params = (
            getattr(self.__class__, 'win_params', None) or {}
        ).copy()
        new_self.request = request
        new_self.context = context
        new_self.set_window_params()
        new_self.create_window()
        new_self._apply_window_params()
        new_self.configure_window()
        return ExtUIScriptResult(
            new_self.win, context=new_self.context)


# =============================================================================
# ObjectListWindowAction
# =============================================================================
class ObjectListWindowAction(BaseWindowAction):
    """
    Базовый Action показа окна списка объектов
    """
    is_select_mode = False
    """Режим показа окна (True - выбор, False - список)"""

    perm_code = 'view'
    """Код доступа"""

    def set_window_params(self):
        params = self.win_params
        params['is_select_mode'] = self.is_select_mode
        params['pack'] = self.parent
        params['title'] = self.parent.title
        params['height'] = self.parent.height
        params['width'] = self.parent.width
        params['read_only'] = getattr(self.parent, 'read_only', None) or (
            not self.has_perm(self.request))

        self.win_params = self.parent.get_list_window_params(
            params, self.request, self.context)

    def create_window(self):
        self.win = self.parent.create_list_window(
            is_select_mode=self.win_params['is_select_mode'],
            request=self.request,
            context=self.context)


# =============================================================================
# ObjectSelectWindowAction
# =============================================================================
class ObjectSelectWindowAction(ObjectListWindowAction):
    """
    Базовый Action показа окна списка выбора объекта из списка

    .. tip:: Используется с m3_ext.ui.fields.complex.ExtDictSelectField
    """
    is_select_mode = True

    def set_window_params(self):
        super(ObjectSelectWindowAction, self).set_window_params()
        # В окне выбора можно только ВЫБИРАТЬ!
        self.win_params['read_only'] = True
        self.win_params['column_name_on_select'] = (
            self.parent.column_name_on_select
        )
        self.win_params['additional_data_names'] = (
            self.parent.additional_data_names
        )


class ObjectMultiSelectWindowAction(ObjectSelectWindowAction):
    """
    Базовый Action показа окна списка выбора нескольких объектов из списка
    """

    def create_window(self):
        self.win = self.parent.multi_select_window()


# =============================================================================
# ObjectEditWindowAction
# =============================================================================
class ObjectEditWindowAction(BaseWindowAction):
    """
    Базовый Action показа окна редактирования объекта.
    """
    perm_code = 'edit'

    def set_window_params(self):
        try:
            obj, create_new = self.parent.get_obj(self.request, self.context)
        except self.parent.get_not_found_exception():
            raise ApplicationLogicException(self.parent.MSG_DOESNOTEXISTS)

        params = self.win_params.copy()
        params['object'] = obj
        params['create_new'] = create_new
        params['form_url'] = self.parent.save_action.get_absolute_url()

        read_only = getattr(self.parent, 'read_only', None) or (
            not self.has_perm(self.request))

        params['read_only'] = read_only
        params['title'] = self.parent.format_window_title(
            u'Просмотр' if read_only else
            u'Добавление' if create_new else
            u'Редактирование'
        )

        self.win_params = self.handle(
            'set_window_params',
            self.parent.get_edit_window_params(
                params, self.request, self.context))

    def create_window(self):
        assert 'create_new' in self.win_params, (
            u'You must call "set_window_params" method of superclass!')
        self.win = self.handle(
            'create_window',
            self.parent.create_edit_window(
                self.win_params['create_new'], self.request, self.context))


# =============================================================================
# ObjectAddWindowAction
# =============================================================================
class ObjectAddWindowAction(ObjectEditWindowAction):
    """
    Базовый Action показа окна добавления объекта.

    .. note::
        Отдельный action для уникальности short_name
    """

    perm_code = 'add'

    pass


# =============================================================================
# ObjectSaveAction
# =============================================================================
class ObjectSaveAction(BaseAction):
    """
    Базовый Action сохранения отредактированного объекта
    """

    class AlreadySaved(Exception):
        """
        Исключение, с помощью которого расширение,
        перекрывшее сохранение объекта,
        может сообщить, что объект сохранен
        и больше ничего делать не нужно.
        """
        pass

    def create_window(self):
        """
        Создаёт окно для дальнейшего биндинга в форму из реквеста
        """
        self.win = self.parent.create_edit_window(
            self.create_new, self.request, self.context)

    def create_obj(self):
        """
        Метод делегирует паку загрузку объекта из БД / создание нового
        объекта модели
        """
        try:
            self.obj, self.create_new = self.parent.get_obj(
                self.request, self.context)
        except self.parent.get_not_found_exception():
            raise ApplicationLogicException(
                self.parent.MSG_DOESNOTEXISTS)

    def bind_win(self):
        """
        Заполнение полей окна по данным из request
        """
        self.win.form.bind_to_request(self.request)

    def bind_to_obj(self):
        """
        Заполнение объекта данными из полей окна
        """
        self.win.form.to_object(self.obj)

    def save_obj(self):
        """
        Сохранение объекта в БД

        :raise: m3.ApplicationLogicException
        """
        # инжекция классов исключений в объект
        self.obj.AlreadySaved = self.AlreadySaved
        try:
            try:
                self.obj = self.handle('save_object', self.obj)
            except self.AlreadySaved:
                # кто-то в цепочке слушателей обработал сохранение объекта
                # и больше ничего делать не нужно
                return
            self.parent.save_row(
                self.obj, self.create_new, self.request, self.context)

            # возможность обработать сохранение подписчиками
            self.handle('post_save', (self.obj, self.context))

        except (exceptions.ValidationError, exceptions.OverlapError) as err:
            raise ApplicationLogicException(six.text_type(err))
        except dj_exceptions.ValidationError as err:
            raise ApplicationLogicException(u'<br/>'.join(err.messages))

    @atomic
    def run(self, request, context):
        """
        Тело Action, вызывается при обработке запроса к серверу

        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext

        .. note::
            Обычно не требует перекрытия
        """
        new_self = copy.copy(self)
        new_self.request = request
        new_self.context = context
        new_self.create_obj()
        new_self.create_window()
        new_self.bind_win()
        new_self.bind_to_obj()
        new_self.save_obj()
        return OperationResult()


# =============================================================================
# ObjectRowsAction
# =============================================================================
class ObjectRowsAction(BaseAction):
    """
    Базовый Action получения данных для отображения в окне списка объектов
    """

    def set_query(self):
        """
        Метод получает первоначальную выборку данных в виде QuerySet
        и помещает в атрибут self.query

        .. note::
            Регистрирует точку расширения `query` в Observer

        """
        self.query = self.handle(
            'query',
            self.parent.get_rows_query(self.request, self.context)
        )

    def apply_search(self):
        """
        Метод применяет к выборке self.query фильтр по тексту
        из поля "Поиск" окна списка

        .. note::
            Регистрирует точку расширения `apply_search` в Observer

        """
        self.query = self.handle(
            'apply_search',
            self.parent.apply_search(
                self.query,
                self.request,
                self.context
            ))

    def apply_filter(self):
        """
        Метод применяет к выборке self.query фильтр, как правило поступающий
        от "колоночных фильтров"/фильтров в контекстных меню в окне списка

        .. note::
            Регистрирует точку расширения `apply_filter` в Observer

        """
        self.query = self.handle(
            'apply_filter',
            self.parent.apply_filter(
                self.query,
                self.request,
                self.context
            ))

    def apply_sort_order(self):
        """
        Метод применяет к выборке self.query сортировку
        по выбранному в окне списка столбцу
        """
        self.query = self.handle(
            'apply_sort_order',
            self.parent.apply_sort_order(
                self.query,
                self.request,
                self.context
            ))

    def apply_limit(self):
        """
        Метод применяет к выборке self.query операцию оганичения
        по количеству элементов (для порционной загрузки в окно списка).
        """
        if getattr(self.parent, 'allow_paging', True):
            offset = extract_int(self.request, 'start')
            limit = extract_int(self.request, 'limit')
        else:
            offset = limit = 0
        self.query = tools.QuerySplitter(self.query, offset, limit)

    def get_rows(self):
        """
        Метод производит преобразование QuerySet в список.
        При этом объекты сериализуются в словари

        :return: Список сериализованных объектов
        :rtype: list
        """
        res = []
        for obj in self.query:
            prep_obj = self.prepare_object(obj)
            if prep_obj:
                res.append(prep_obj)
            else:
                self.query.skip_last()
        return self.handle('get_rows', res)

    def prepare_object(self, obj):
        """
        Возвращает словарь, для составления результирующего списка

        :param obj: Объект, полученный из QuerySet'a
        :type obj: django.db.models.Model
        :return: Словарь для сериализации в json
        :rtype: dict

        .. note::

            Регистрирует в Observer точку расширения `prepare_obj`

        """
        if hasattr(self.parent, 'prepare_row'):
            obj = self.parent.prepare_row(obj, self.request, self.context)
        if obj is None:
            return None

        result_dict = {}

        def parse_data_indexes(obj, col, result):
            # сплит строки вида "asdad[.asdasd]" на "голову" и "хвост"
            # "aaa" -> "aaa", None
            # "aaa.bbb.ccc" -> "aaa", "bbb.ccc"
            col, subcol = (col.split('.', 1) + [None])[:2]
            # ------- если есть подиндекс - идем вглубь
            if subcol:
                try:
                    obj = getattr(obj, col, None)
                except dj_exceptions.ObjectDoesNotExist:
                    obj = None
                sub_dict = result.setdefault(col, {})
                parse_data_indexes(obj, subcol, sub_dict)
            else:
                # --- подиндекса нет - получаем значение
                # ищем поле в модели
                if obj:
                    opts = ModelOptions(obj)
                    try:
                        fld = opts.get_field_by_name(col)[0]
                    except (AttributeError, IndexError,
                            dj_fields.FieldDoesNotExist):
                        fld = None
                else:
                    fld = None
                # получаем значение
                try:
                    obj = getattr(obj, col, None)
                except dj_exceptions.ObjectDoesNotExist:
                    obj = None
                if fld:
                    try:
                        obj = obj.display()
                    except AttributeError:
                        # аттрибут choises существует у Field
                        # но отсутствует у RelatedObject
                        if hasattr(fld, 'choices') and fld.choices:
                            # если получаемый атрибут - поле, имеющее choices
                            # пробуем найти соответствующий значению вариант
                            for ch in fld.choices:
                                if obj == ch[0]:
                                    obj = ch[1]
                                    break
                            else:
                                obj = u''

                else:
                    # атрибут (не поле) может быть вызываемым
                    if callable(obj):
                        obj = obj()

                if isinstance(obj, datetime.datetime):
                    obj = '%02d.%02d.%04d %02d:%02d:%02d' % (
                        obj.day, obj.month, obj.year,
                        obj.hour, obj.minute, obj.second
                    )
                elif isinstance(obj, datetime.date):
                    obj = '%02d.%02d.%04d' % (obj.day, obj.month, obj.year)

                if obj is None:
                    # None выводится пустой строкой
                    obj = u''

                if not isinstance(obj, (int, bool)):
                    obj = force_text(obj)
                result[col] = obj

        # заполним объект данными по дата индексам
        for col in self.get_column_data_indexes():
            parse_data_indexes(obj, col, result_dict)

        return self.handle('prepare_obj', result_dict)

    def get_total_count(self):
        """
        Возвращает общее кол-во объектов

        :return: Количество объектов в выборке
        :rtype: int
        """
        return self.query.count()

    def get_column_data_indexes(self):
        """
        :return: Список data_index колонок, для формирования json
        :rtype: list
        """
        res = ['__unicode__' if six.PY2 else '__str__', ]
        for col in getattr(self.parent, '_columns_flat', []):
            res.append(col['data_index'])
        res.append(self.parent.id_field)
        return res

    def handle_row_editing(self, request, context, data):
        """
        Обрабатывает inline-редактирование грида
        Метод должен вернуть кортеж (удачно/неудачно, "сообщение"/None)

        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        :param data: Данные редактирования
        :type data: dict
        :return: (True/False, message/None)
        :rtype: tuple

        """
        return self.handle(
            'row_editing',
            self.parent.handle_row_editing(request, context, data)
        )

    def run(self, request, context):
        new_self = copy.copy(self)
        new_self.request = request
        new_self.context = context

        request_params = get_request_params(request)
        if request_params.get('xaction') not in ['read', None]:
            data = json.loads(request_params.get('rows'))
            if not isinstance(data, list):
                data = [data]
            success, message = self.handle_row_editing(
                request=request,
                context=context,
                data=data)
            result = OperationResult(success=success, message=message)
        else:
            new_self.set_query()
            new_self.apply_search()
            new_self.apply_filter()
            new_self.apply_sort_order()
            total_count = new_self.get_total_count()
            new_self.apply_limit()
            rows = new_self.get_rows()
            result = PreJsonResult({
                'rows': rows,
                'total': total_count
            })
        return result


# =============================================================================
# ObjectDeleteAction
# =============================================================================
class ObjectDeleteAction(BaseAction):
    """
    Действие по удалению объекта
    """
    perm_code = 'delete'

    def try_delete_objs(self):
        """
        Удаляет обекты и пытается перехватить исключения

        :except: m3.RelatedError, django.db.utils.IntegrityError:
        :raise: m3.ApplicationLogicException
        """
        # TODO: разгрести этот УЖАС!
        try:
            self.delete_objs()
        except RelatedError as e:
            raise ApplicationLogicException(e.args[0])
        except Exception as e:
            if e.__class__.__name__ == 'IntegrityError':
                message = (
                    u'Не удалось удалить элемент. '
                    u'Возможно на него есть ссылки.')
                raise ApplicationLogicException(message)
            else:
                # все левые ошибки выпускаем наверх
                raise

    def delete_objs(self):
        """
        Удаляет обекты по ключам из контекста
        """
        ids = getattr(self.context, self.parent.id_param_name)
        for i in ids:
            self.delete_obj(i)

    def audit(self, obj):
        """
        Обработка успешно удалённых объектов
        """
        pass

    def delete_obj(self, id_):
        """
        Удаление объекта по идентификатору @id_

        :param id_: Идентификатор объекта
        """
        obj = self.parent.delete_row(id_, self.request, self.context)
        self.audit(obj)

    def run(self, request, context):
        new_self = copy.copy(self)
        new_self.request = request
        new_self.context = context
        new_self.try_delete_objs()
        return OperationResult()


# =============================================================================
# BasePack
# =============================================================================
class BasePack(ActionPack):
    """
    Потомок ActionPack, реализующий автогенерацию short_name, url
    """

    def declare_context(self, action):
        """
        Декларация контекста для экшна

        .. code::

            def declare_context(self, action):
                if action is self.do_right_things_action:
                    return {
                        'things': {'type': 'list'},
                        'done': {'type': 'boolean'}
                    }
        """
        return {}

    # @classmethod
    # def get_short_name(cls):
    # """
    # Имя пака для поиска в ControllerCache
    # """
    # name = cls.__dict__.get('_auto_short_name')
    # if not name:
    # name = '%s/%s' % (
    # inspect.getmodule(cls).__name__.replace(
    # '.actions', ''
    # ).replace(
    # '.', '/').lower(),
    # cls.__name__.lower())
    # cls._auto_short_name = name
    # return name

    # @property
    # @tools.cached_to('__cached_short_name')
    # def short_name(self):
    #     # имя пака для поиска в ControllerCache в виде атрибута
    #     # для совместимости с m3
    #     return self.get_short_name()

    @property
    def url(self):
        """
        Относительный url пака
        """
        return r'/%s' % self.short_name

    @classmethod
    def absolute_url(cls):
        """
        Получение url для построения внутренних кэшей m3
        """
        path = [r'/%s' % cls.get_short_name()]
        pack = cls.parent
        while pack is not None:
            path.append(pack.url)
            pack = pack.parent
        for cont in ControllerCache.get_controllers():
            p = cont.find_pack(cls)
            if p:
                path.append(cont.url)
                break
        return ''.join(reversed(path))


# =============================================================================
# ObjectPack
# =============================================================================
class ObjectPack(BasePack, IMultiSelectablePack):
    """
    Пак с экшенам, реализующими специфичную для работы с моделью действиями по
    добавлению, редактированию, удалению (CRUD actions)

    .. note::
        Можно из пака включить добавление элементов в главное меню или на
        десктоп extjs. По умолчанию эта опция выключена

        .. code::

            add_to_desktop = True
            add_to_menu = True

        Если методы extend_menu/extend_desktop не реализованы,
        меню будет расширяться на основе title и get_default_action

        Методы extend_X приоритетны

        .. code::

            def extend_menu(self, menu):
                \"\"\"
                Расширение главного меню.
                \"\"\"
                return (
                    # добавление пунктов в меню "справочники"
                    menu.dicts(
                        menu.Item(u'Dict 1', self),
                        menu.SubMenu(u'Dict SubMenu',
                            menu.Item(u'Dict 2', self.some_action),
                        ),
                    ),
                    # добавление пунктов в меню "реестры"
                    menu.registries(
                        menu.Item(u'Reg 1'),
                        menu.SubMenu(u'Regs SubMenu',
                            menu.Item(u'Reg 2'),
                        ),
                    ),
                    # добавление пунктов в меню "администрирование"
                    menu.administry(
                        menu.Item(u'Admin item 1')
                    ),

                    # добавление пунктов в "корень" меню
                    menu.Item(name=u'item 1', self.some_action),

                    # добавление подменю в "корень" меню
                    menu.SubMenu(u'SubMenu',
                        menu.Item(u'Item 2', self.some_action),
                        menu.SubMenu(u'SubSubMenu',
                            menu.Item(u'Item 3', self.some_action),
                        ),
                    ),
                )

        Пустые подменю автоматически "схлопываются" (не видны в Главном Меню)

        .. code::

            def extend_desktop(self, desk):
                \"\"\"
                Расширение Рабочего Стола
                \"\"\"

                return (
                   desk.Item(u'Ярлык 1', pack=self.list_action),
                   ...
                )

        Любой из элементов можно отключить вернув вместо него None. Например::

            desk.Item(u'Name', pack=self) if some_condition else None

    """

    column_constructor_fabric = ui.ColumnsConstructor.from_config
    """
    Фабрика колонок по данным атрибута 'columns'

    .. note::

        callable-объект, возвращающий объект с методом 'configure_grid(grid)'
    """

    @property
    def title(self):
        """
        Заголовок окна справочника, если не перекрыт
        в потомках - берется из модели
        """
        return six.text_type(
            self.model._meta.verbose_name_plural or
            self.model._meta.verbose_name or
            repr(self.model)).capitalize()

    model = None
    """
    Класс django-модели, для которой будет формироваться справочник
    """

    columns = [
        {
            'header': u'Наименование',
            'data_index': '__unicode__' if six.PY2 else '__str__',
        },
    ]
    """
    Список колонок для добавления в грид, data_index - поле или метод модели

    .. important::
        Для корректной работы полей выбора, необходима \
        колонка с data_index = '__unicode__'

    .. code::

        columns = [
            {
                'data_index: '__unicode__',
                'hidden': True,
            },
            {
               'data_index':'',
               'width':,
               'header':u'',
               'serchable':True,
               'sortable':True,
               'sort_fields': ('foo','bar'),
            },
            {
               'header':u'Группирующая Колонка 1',
               'columns': [
                   {
                       'data_index':'school.name',
                       'width':200,
                       'header':u'Колонка 1',
                       'searchable':True,
                       'search_fields': ('school.fullname',),
                   },
               ]
            },
            {
               'data_index':'school.parent.name',
               'width':200,
               'header':u'Родитель',
               'renderer':'parent_render'
               'select_related': ('parent',),
            },
        ]
    """

    select_related = None
    """
    Перечень related полей, для передачи в Manager.select_related.

    Если None и в columns не будет найдено related полей, то в rows_action
    select_related не будет выполняться.

    Если любая пустая коллекция, то вызовется select_related без параметров,
    что может сказаться на производительности
    """

    filter_engine_clz = filters.MenuFilterEngine
    """
    Класс конструктора фильтра для грида

    .. note::

        Подробнее смотри в objectpack.demo
    """

    @property
    def id_param_name(self):
        """
        :return: Название поля, идентифицирующего объект и название параметра,
                 который будет передаваться в запросе на модификацию/удаление
        :rtype: str
        """
        return '%s_id' % self.short_name

    id_field = 'id'
    """
    data_index колонки, идентифицирующей объект.
    Этот параметр будет браться из модели и передаваться как ID
    в ExtDataStore, т.е в post запросе редактирования будет
    лежать :code:`{id_param_name: obj.id_field}`
    """

    column_name_on_select = '__unicode__' if six.PY2 else '__str__'
    """
    Поле/метод, предоставляющее значение для отображения в ExtDictSelectField

    .. attention::

        ПОКА НЕ РАБОТАЕТ извлечение вложенных полей - конфликт с ExtJS
    """
    additional_data_names = []
    """
    Дополнительные атрибуты строки, которые будут переданы в обработчик
    afterselect соответствующего поля ExtDictSelectField
    """

    search_fields = None
    """
    Список дополнительных полей модели по которым будет идти поиск
    основной список береться из colums по признаку searchable
    """

    allow_paging = True
    """
    Включить пагинацию
    """

    _DEFAULT_PAGING_START = 0
    """
    Декларируемое значение сдвига начала пагинации по-умолчанию
    при allow_paging=True и непереданном клиентом значения `start`
    """
    _DEFAULT_PAGING_LIMIT = 25
    """
    Декларируемое значение количества записей при пагинации по-умолчанию
    при allow_paging=True и непереданном клиентом значения `limit`
    """
    read_only = False
    """
    Пак будет настраивать грид на возможность редактирования
    """

    list_sort_order = None
    """
    Порядок сортировки элементов списка. Работает следующим образом:

    - Если в list_columns модели списка есть поле
      code, то устанавливается сортировка по
      возрастанию этого поля
    - Если в list_columns модели списка нет поля
      code, но есть поле name, то устанавливается
      сортировка по возрастанию поля name

    .. code::

        list_sort_order = ['code', '-name']
    """

    add_window = None
    """
    Окно для добавления элемента справочника
    """

    edit_window = None
    """
    Окно для редактирования элемента справочника
    """

    can_delete = None
    """
    Флаг разрешающий/запрещающий удаление. Если None, то удаление возможно,
    при наличии add_window/edit_window
    """

    list_window = ui.BaseListWindow
    """
    Класс отвечающий за отображение окна со списком объектов
    """

    select_window = ui.BaseSelectWindow  # Форма выбора
    """
    Класс отвечающий за отображение окна выбора из списка объектов
    """

    multi_select_window = ui.BaseMultiSelectWindow  # Форма выбора
    """
    Класс отвечающий за отображение окна множественного выбора
    из списка объектов
    """

    width, height = 600, 400
    """
    Размеры окна по умолчанию
    """

    MSG_DOESNOTEXISTS = (
        u'Запись не найдена в базе данных.<br/>'
        u'Возможно, она была удалена. Пожалуйста, обновите таблицу!'
    )

    _all_search_fields = None  #: Плоский список полей фильтрации

    _sort_fields = None  #: Словарь data_index:sort_order

    _is_primary_for_model = True
    """
    Признак того, что Pack является основным для модели

    .. note::

        по основному паку строятся контролы ExtDictSelectField
        при автогонерации окон редактирования
    """

    @staticmethod
    def _get_model_pack(model_name):
        """
        функция, возвращающая экземпляр Pack, для укзанной по имени модели.

        .. note::

            Реализация функции инжектируется при регистрации
            в Observable контроллер.

        :param model_name: Имя модели
        :type model_name: str
        :return:
        :rtype: objectpack.ObjectPack
        """
        return None

    def __init__(self):
        super(ObjectPack, self).__init__()
        # В отличие от обычных паков в этом экшены создаются самостоятельно,
        # а не контроллером
        # Чтобы было удобно обращаться к ним по имени
        #: Экшен показа окна со списком объектов
        self.list_window_action = ObjectListWindowAction()
        #: Экшен показа окна со списком для выбора объектов
        self.select_window_action = ObjectSelectWindowAction()
        #: Экшен с получения данных объектов / редактирование строк
        self.multi_select_window_action = ObjectMultiSelectWindowAction()
        #: Экшен с получения данных объектов / редактирование строк
        self.rows_action = ObjectRowsAction()
        # Но привязать их все равно нужно
        self.actions.extend([
            self.list_window_action,
            self.select_window_action,
            self.multi_select_window_action,
            self.rows_action
        ])
        if self.add_window and not self.read_only:
            #: Экшен показа окна добавления объекта
            self.new_window_action = ObjectAddWindowAction()
            self.actions.append(self.new_window_action)
        else:
            self.new_window_action = None

        if self.edit_window and not self.read_only:
            #: Экшен показа окна редактирования объекта
            self.edit_window_action = ObjectEditWindowAction()
            self.actions.append(self.edit_window_action)
        else:
            self.edit_window_action = None

        if (self.add_window or self.edit_window) and not self.read_only:
            #: Экшен сохранения объекта
            self.save_action = ObjectSaveAction()
            self.actions.append(self.save_action)
        else:
            self.save_action = None

        if self.can_delete is None:
            self.can_delete = (
                self.add_window or self.edit_window) and not self.read_only
        if self.can_delete:
            #: Экшен удаления объектовы
            self.delete_action = ObjectDeleteAction()
            self.actions.append(self.delete_action)
        else:
            self.delete_action = None

        # построение плоского списка колонок
        self._columns_flat = []
        self._all_search_fields = (self.search_fields or [])[:]
        self._sort_fields = {}
        self._select_related_fields = (self.select_related or [])[:]

        def flatify(cols):
            for c in cols:
                sub_cols = c.get('columns', None)
                if sub_cols is not None:
                    flatify(sub_cols)
                else:
                    self._columns_flat.append(c)
                    data_index = c['data_index']
                    field = data_index.replace('.', '__')
                    # поле(поля) для сортировки
                    if c.get('sortable', False):
                        sort_fields = c.get('sort_fields', [field])
                        try:
                            sort_fields = list(sort_fields)
                        except TypeError:
                            sort_fields = [sort_fields]
                        self._sort_fields[data_index] = sort_fields
                    # поле для фильтрации
                    if c.get('searchable'):
                        search_fields = c.get('search_fields', [field])
                        try:
                            search_fields = list(search_fields)
                        except TypeError:
                            search_fields = [search_fields]
                        self._all_search_fields.extend(search_fields)
                    # related fields
                    related_fields = c.get("select_related")
                    if not related_fields:
                        lookup = "__".join(tools.get_related_fields(
                            self.model, data_index.split(".")))
                        related_fields = lookup and [lookup] or []
                    try:
                        related_fields = list(related_fields)
                    except TypeError:
                        related_fields = [related_fields]
                    for f in related_fields:
                        if f not in self._select_related_fields:
                            self._select_related_fields.append(f)

        flatify(self.get_columns())

        # подключение механизма фильтрации
        self._filter_engine = self.filter_engine_clz([
            (c['data_index'], c['filter'])
            for c in self._columns_flat
            if 'filter' in c
        ])

    def replace_action(self, action_attr_name, new_action):
        """
        Заменяет экшен в паке

        :param action_attr_name: Имя атрибута пака для экшена
        :type action_attr_name: str
        :param new_action: Экземпляр экшена
        :type new_action: objectpack.BaseAction
        """
        if getattr(self, action_attr_name, None):
            self.actions.remove(getattr(self, action_attr_name))
        setattr(self, action_attr_name, new_action)
        if getattr(self, action_attr_name):
            self.actions.append(getattr(self, action_attr_name))

    def declare_context(self, action):
        """
        Декларирует контекст для экшна

        :param action: Экземпляр экшена
        :type action: objectpack.BaseAction
        :return: Правила для декларации контекста DeclarativeActionContext
        :rtype: dict
        """
        result = super(ObjectPack, self).declare_context(action)
        if action in (
            self.edit_window_action,
            self.new_window_action,
            self.save_action
        ):
            result = {self.id_param_name: {'type': tools.int_or_zero}}
        elif action is self.delete_action:
            result = {self.id_param_name: {'type': tools.int_list}}
        elif action is self.rows_action:
            if self.allow_paging:
                result.update(
                    start={
                        'type': 'int',
                        'default': self._DEFAULT_PAGING_START
                    },
                    limit={
                        'type': 'int',
                        'default': self._DEFAULT_PAGING_LIMIT
                    }
                )
        return result

    def get_default_action(self):
        """
        Возвращает действие по умолчанию
        (действие для значка на раб.столе/пункта меню)

        .. note::
            Используется пи упрощенном встраивании в UI (add_to_XXX=True)

        :return: Экземпляр экшена
        :rtype: objectpack.BaseAction
        """
        return self.list_window_action

    def get_display_text(self, key, attr_name=None):
        """
        Возвращает отображаемое значение записи
        (или атрибута attr_name) по ключу key

        :param key: ID объекта
        :type key: basestring or int
        :param attr_name: Имя атрибута модели
        :type attr_name: str
        :return: Отображаемое текстовое представление объекта
        :rtype: basestring
        """
        try:
            row = self.get_row(key)
        except self.model.DoesNotExist:
            row = None

        if row is not None:
            try:
                text = getattr(row, attr_name)
            except AttributeError:
                try:
                    text = getattr(row, self.column_name_on_select)
                except AttributeError:
                    raise Exception(
                        u'Не получается получить поле {0} для '
                        u'DictSelectField.pack = {1}'.format(
                            attr_name, self)
                    )

            # getattr может возвращать метод, например verbose_name
            if callable(text):
                return text()
            else:
                return six.text_type(text)

    def get_edit_window_params(self, params, request, context):
        """
        Возвращает словарь параметров,
        которые будут переданы окну редактирования

        .. code::

            def get_edit_window_params(self, params, request, context):
                params = super(RightThingsPack, self).get_edit_window_params(
                    params, request, context)
                params.update({
                    'user': request.user,
                    'height': 800,
                    'width': 600,
                })
                return params

        :param params: Словарь параметров
        :type params: dict
        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Словарь параметров
        :rtype: dict
        """
        return params

    def get_list_window_params(self, params, request, context):
        """
        Возвращает словарь параметров,
        которые будут переданы окну списка

        .. code::

            def get_list_window_params(self, params, request, context):
                params = super(RightThingsPack, self).get_list_window_params(
                    params, request, context)
                params.update({
                    'title': u'Right things done by user: %s'
                    % request.user.username,
                    'height': 800,
                    'width': 600,
                })
                return params

        :param params: Словарь параметров
        :type params: dict
        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Словарь параметров
        :rtype: dict
        """
        return params

    def format_window_title(self, action):
        """
        Возвращает отформатированный заголовка окна.
        Заголовок примет вид "Модель: Действие"

        .. hint:: Например "Сотрудник: Добавление"

        :param action: Действие характеризующее экшен
        :type action: unicode
        :return: Заголовок окна
        :rtype: unicode
        """
        return "%s: %s" % (self.model._meta.verbose_name.capitalize(), action)

    # ==================== ФУНКЦИИ ВОЗВРАЩАЮЩИЕ АДРЕСА =====================
    def get_list_url(self):
        """
        Возвращает адрес формы списка элементов справочника.

        .. note::
            Используется для присвоения адресов в прикладном приложении

        :return: url экшена показа окна со списком объектов
        :rtype: str
        """
        return self.list_window_action.get_absolute_url()

    def get_select_url(self):
        """
        Возвращает адрес формы выбора из списка элементов справочника.

        .. note::
            Используется для присвоения адресов в прикладном приложении

        :return: url экшена показа окна выбора из списка объектов
        :rtype: str
        """
        return self.select_window_action.get_absolute_url()

    def get_multi_select_url(self):
        """
        Возвращает адрес формы выбора из списка элементов справочника.

        .. note::
            Используется для присвоения адресов в прикладном приложении

        :return: url экшена показа окна выбора из списка объектов
        :rtype: str
        """
        return self.multi_select_window_action.get_absolute_url()

    def get_edit_url(self):
        """
        Возвращает адрес формы редактирования элемента справочника

        :return: url экшена показа окна редактирования объекта
        :rtype: str
        """
        if self.edit_window_action:
            return self.edit_window_action.get_absolute_url()

    def get_rows_url(self):
        """
        Возвращает адрес, по которому запрашиваются элементы грида

        :return: url экшена с данными для грида
        :rtype: str
        """
        return self.rows_action.get_absolute_url()

    def get_autocomplete_url(self):
        """
        Возвращает адрес для запроса элементов,
        подходящих введенному в поле тексту

        :return: url экшена
        :rtype: str
        """
        return self.get_rows_url()

    def get_display_dict(self, key, value_field='id', display_field='name'):
        key, value_field, display_field
        return []

    def get_not_found_exception(self):
        """
        Возвращает класс исключения 'объект не найден'

        :return: Класс исключения модели django
        :rtype: django.core.exceptions.ObjectDoesntExist
        """
        return self.model.DoesNotExist

    def get_columns(self, *args, **kwargs):
        """Возвращает набор колонок для конфигурирования грида.

        Добавлено для возможности проводить кастомизацию колонок
        на основе переданных параметров.
        """
        return self.columns

    def configure_grid(self, grid, *args, **kwargs):
        """
        Конфигурирует grid для работы с этим паком,
        создает колонки и задает экшены

        .. hint::
            Удобно использовать в окнах в комбинированных справочниках
            с несколькими гридами

        .. code::

            class RightThingsWindow(objectpack.BaseWindow):

                def _init_components(self):
                    super(RightThingsWindow, self)._init_components()
                    ...
                    self.right_things_todo_grid = ext.ExtObjectGrid()
                    self.right_things_done_grid = ext.ExtObjectGrid()

                def _do_layout(self):
                    ...

                def set_params(self, params):
                    super(RightThingsWindow, self).set_params(params)
                    ...
                    get_pack_instance('RightThingsTodoPack').configure_grid(
                        self.right_things_todo_grid)
                    get_pack_instance('RightThingsDonePack').configure_grid(
                    self.right_things_done_grid)

        :param grid: Грид
        :type grid: m3_ext.ui.panels.grids.ExtObjectGrid
        """
        def get_url(x):
            return x.get_absolute_url() if x else None

        grid.url_data = get_url(self.rows_action)
        if not self.read_only:
            grid.url_new = get_url(self.new_window_action)
            grid.url_edit = get_url(self.edit_window_action)
            grid.url_delete = get_url(self.delete_action)

        columns = self.get_columns(*args, **kwargs)
        # построение колонок классом-констуктором
        cc = self.column_constructor_fabric(
            config=columns,
            ignore_attrs=[
                'searchable',
                'search_fields',
                'sort_fields',
                'filter'
            ])
        cc.configure_grid(grid)

        if self.get_search_fields():
            grid.add_search_field()

        grid.row_id_name = self.id_param_name
        grid.allow_paging = self.allow_paging
        grid.store.remote_sort = self.allow_paging

        self._filter_engine.configure_grid(grid)

    def create_edit_window(self, create_new, request, context):
        """
        Получить окно редактирования / создания объекта

        :param create_new: Признак добавления или редактирования
        :type create_new: bool
        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Окно добавления/редактирования
        :rtype: objectpack.ui.BaseEditWindow

        .. hint::
            Удобно использовать для добавления/конфигурирования кастомных
            контролов в окно

        .. code::

            def create_edit_window(self, create_new, request, context):
                win = super(RightThingsPack, self).create_edit_window(
                    create_new, request, context)
                win.top_bar.btn_do_right_thing

        """
        if create_new:
            return self.add_window()
        else:
            return self.edit_window()

    def create_list_window(self, is_select_mode, request, context):
        """
        Получить окно списка / выбора объектов

        :param is_select_mode: Режим показа окна (True - выбор, False - список)
        :type is_select_mode: bool
        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Окно списка/выбора объектов
        :rtype: objectpack.ui.BaseListWindow
        """
        if is_select_mode:
            return self.select_window()
        else:
            return self.list_window()

    def handle_row_editing(self, request, context, data):
        """
        Метод принимает данные из редактируемого грида и возвращает
        результат редактирования кортежем вида
        (удачно/неудачно, "сообщение"/None)
        :param request:
        :type request: django.http.HttpRequest
        :param context:
        :type context: m3.actions.context.DeclarativeActionContext
        :param data:
        :type data:
        """
        return False, None

    def get_rows_query(self, request, context):
        """
        Возвращает выборку из БД для получения списка данных

        :param request: Запрос
        :type request: django.http.HttpRequest
        :param context: Контекст
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Кварисет
        :rtype: django.db.models.query.QuerySet

        .. code::

            def get_rows_query(self, request, context):
                query = super(RightThingsDonePack, self).get_rows_query(
                    request, context)
                return query.filter(done=True)

        """
        query = self.model.objects.all()
        if self._select_related_fields or self.select_related is not None:
            query = query.select_related(*self._select_related_fields)
        return query

    def get_search_fields(self, request=None, context=None):
        """
        :param request:
        :type request: django.http.HttpRequest
        :param context:
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Список значений 'data_index' из колонок self.columns,
                 по которым будет производиться поиск
        :rtype: list

        .. note::
            Обычно не требует перекрытия

        """
        return self._all_search_fields[:]

    def get_sort_order(self, data_index, reverse=False):
        """
        :param data_index
        :type data_index: str
        :param reverse: Обратный порядок
        :type reverse: bool
        :return: Ключи сортировки для указанного data_index
        :rtype: list or tuple

        .. note::
            Обычно не требует перекрытия

        """
        sort_order = self._sort_fields[data_index]
        if reverse:
            sort_order = ['-%s' % s for s in sort_order]
        return sort_order

    def apply_filter(self, query, request, context):
        """
        Применяет фильтрацию к выборке query

        :param query:
        :type query: django.db.models.query.QuerySet
        :param request:
        :type request: django.http.HttpRequest
        :param context:
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Отфильтрованная выборка query
        :rtype: django.db.models.query.QuerySet

        .. note::
            Обычно не требует перекрытия

        """
        return self._filter_engine.apply_filter(query, request, context)

    def apply_search(self, query, request, context):
        """
        Возвращает переданную выборку отфильторованной по параметрам запроса

        :param query:
        :type query: django.db.models.query.QuerySet
        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        :return:
        :rtype: django.db.models.query.QuerySet

        .. note::
            Обычно не требует перекрытия

        """
        return apply_search_filter(
            query,
            get_request_params(request).get('filter'),
            self.get_search_fields()
        )

    def apply_sort_order(self, query, request, context):
        """
        Возвращает переданную выборку отсортированной по параметрам запроса

        :param query:
        :type query:
        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        :return:
        :rtype:

        .. note::
            Обычно не требует перекрытия

        """
        request_params = get_request_params(request)
        sorting_key = request_params.get('sort')
        if sorting_key:
            reverse = request_params.get('dir') == 'DESC'
            sort_order = self.get_sort_order(
                data_index=sorting_key,
                reverse=reverse)
            query = query.order_by(*sort_order)
        else:
            query = self.apply_default_sort_order(query)
        return query

    def apply_default_sort_order(self, query):
        """
        :param query:
        :type query: django.db.models.query.QuerySet
        :return: Выборка, отсортированная по-умолчанию
        :rtype: django.db.models.query.QuerySet

        .. note::
            Обычно не требует перекрытия

        """
        if self.list_sort_order:
            query = query.order_by(*self.list_sort_order)
        return query

    def prepare_row(self, obj, request, context):
        """
        Установка дополнительных атрибутов объекта
        перед возвратом json'a строк грида
        или может вернуть proxy_object

        :param obj: Объект из выборки, полученной в get_rows_query
        :type obj: django.db.models.Model
        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        :return:
        :rtype:

        .. code::

            columns = [
                {
                    'data_index': 'title',
                    'header': 'Title',
                },
                {
                    'data_index': 'date',
                    'header': 'Date',
                },
                {
                    'data_index': 'done_checkbox',
                    'header': 'Done',
                }
            ]

            def prepare_row(self, obj, request, context):
                \"\"\"
                Добавляет в объект атрибут, для отображения булевого
                поля модели как чек-бокс
                \"\"\"
                obj = super(RightThingsPack, self).prepare_row(
                    obj, request, context)
                obj.done_checkbox = (
                    '<div class="x-grid3-check-col-on%s"></div>'
                     % '-on' if obj.done else ''
                )
        """
        return obj

    def get_row(self, row_id):
        """
        Функция возвращает объект по :row_id
        Если id нет, значит нужно создать новый объект

        .. note::

            Используется в ExtDictSelectField'ax

        :param row_id: id объекта
        :type row_id: int
        :return: Объект модели self.model
        :rtype: django.db.models.Model
        """
        if row_id == 0:
            record = self.model()
        else:
            record = self.model.objects.get(id=row_id)
        return record

    def get_obj(self, request, context):
        """
        Получает id объекта из контекста и возвращает
        кортеж (объект модели, create_new), где create_new признак
        создания или редактирования

        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        :return: (Объект модели self.model, create_new)
        :rtype: tuple
        """
        obj_id = getattr(context, self.id_param_name)
        create_new = (obj_id == 0)
        record = self.get_row(obj_id)
        return record, create_new

    def save_row(self, obj, create_new, request, context):
        """
        Сохраняет объект.
        При необходимости возбуждается ValidationError, или OverlapError,
        которые затем отлавливаются в ObjectSaveAction.save_obj

        :param obj: Объект модели self.model
        :type obj: django.db.models.Model
        :param create_new: Признак создания нового объекта
        :type create_new: bool
        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        """
        obj.save()

    def delete_row(self, obj_id, request, context):
        """
        Удаляет объект по :obj_id
        Возвращает удалённый объект - т.е. объект модели,
        который уже не представлен в БД

        :param obj_id: pk объекта
        :type obj_id: int
        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Удалённый объект
        :rtype: django.db.models.Model
        """
        try:
            obj = self.model.objects.get(id=obj_id)
        except self.get_not_found_exception():
            raise ApplicationLogicException(self.MSG_DOESNOTEXISTS)
        result = True
        if hasattr(obj, 'safe_delete'):
            result = obj.safe_delete()
        else:
            result = safe_delete(obj)
        # в случае успеха safe_delete возвращет true
        if not result:
            raise RelatedError(
                u'Не удалось удалить элемент {0}. '
                u'Возможно на него есть ссылки.'.format(obj_id))
        return obj

    def get_filter_plugin(self):
        """
        Возвращает плагин фильтрации

        :return: js-код с плагином фильтрации
        :rtype: basestring
        """
        filter_items = []
        list_columns_filter = dict(
            (column['data_index'], column['filter'])
            for column in self._columns_flat
            if column.get('filter') and not column.get('columns'))
        if list_columns_filter:
            for k, v in list_columns_filter.items():
                params = {
                    'type': v.get('type', 'string'),
                    'data_index': k
                }
                f_options = v.get('options', [])
                if callable(f_options):
                    f_options = f_options()
                params['options'] = "[%s]" % ','.join(
                    (("'%s'" % item)
                     if isinstance(item, six.string_types) else
                     ((item is None and '[]') or ("['%s','%s']" % item)))
                    for item in f_options)
                filter_items.append("""{
                    type:'%(type)s',
                    dataIndex:'%(data_index)s',
                    options:%(options)s
                }""" % params)
            return """
                 new Ext.ux.grid.GridFilters({filters:[%s]})
            """ % ','.join(filter_items)


# =============================================================================
# SelectorWindowAction
# =============================================================================
class SelectorWindowAction(BaseAction):
    """
    Экшн показа окна выбора с пользовательским экшном обработки выбранных
    элементов. Например, множественный выбор элементов справочника, для
    последующего создания связок с ними.
    """
    url = r'/selector_window'
    """
    Жестко определяет url для экшена

    TODO: выпылить, использовать проперти из BaseAction
    """

    multi_select = True
    """
    Признак показа окна множественного выбора
    """

    callback_url = None
    """
    url экшна обработки результата выбора
    """

    data_pack = None
    """
    Пак, объекты модели которого выбираются
    """

    def configure_action(self, request, context):
        """
        Настройка экшна. Здесь нужно назначать пак и callback

        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext

        .. code::

            def configure_action(self, request, context):
                super(UserPack, self).configure_action(request, context)
                self.data_pack = get_pack_instance('GroupPack')
                self.callback_url = (
                    self.parent.selector_save_action.get_absolute_url())

        """
        pass

    def configure_context(self, request, context):
        """
        В данном методе происходит конфигурирование контекста для окна выбора.
        Возвращаемый результат должен быть экземпляром ActionContext.

        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        :rtype: m3.actions.context.ActionContext
        """
        return ActionContext()

    def configure_window(self, win, request, context):
        """
        В данном методе происходит конфигурирование окна выбора

        :param win: Окно выбора из справочника
        :type win: objectpack.ui.BaseSelectWindow
        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        """
        return win

    def run(self, request, context):
        """
        Выполнение экшна

        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Результат с окном ExtJS
        :rtype: m3_ext.ui.results.ExtUIScriptResult
        :raise: AssertionError, m3.ApplicationLogicException

        .. note::
            Без крайней необходимости не перекрывать
        """
        new_self = copy.copy(self)

        new_self.configure_action(request, context)

        assert new_self.data_pack, u'Не задан ActionPack-источник данных!'

        new_context = new_self.configure_context(request, context)

        # вызов экшна показа окна выбора
        win_result = new_self.data_pack.select_window_action.run(
            request, context)
        win = getattr(win_result, 'data', None)
        if not win:
            return win_result

        if not isinstance(win, ui.BaseSelectWindow):
            raise ApplicationLogicException(
                u'Класс окна выбора должен быть потомком BaseSelectWindow!')

        win = new_self.configure_window(win, request, context)

        win.callback_url = new_self.callback_url

        if new_self.multi_select:
            win.multi_select = True
            win._enable_multi_select()

        return ExtUIScriptResult(win, new_context)


def multiline_text_window_result(data, success=True, title=u'', width=600,
                                 height=500):
    """
    Формирование OpersionResult в виде многострочного окна,
    с размерами :width x :height и заголовком :title,
    отображающего текст :data

    :param data: Текст или список со строками
    :type data: basestring or Iterable
    :param success: Результат выполнения операции в контексте ExtJS
    :type success: bool
    :param title: Заголовок окна
    :type title: basestring
    :param width: Ширина окна
    :type width: int
    :param height: Высота окна
    :type height: int
    :return: Результат операции в контексте ExtJS
    :rtype: m3.actions.results.OperationResult
    """
    if not isinstance(data, six.string_types):
        data = u'\n'.join(data)
    return OperationResult(
        success=success,
        code=(
            u"""
            (function() {
                var msg_win = new Ext.Window({
                    title: '%s',
                    width: %s, height: %s, layout:'fit',
                    items:[
                        new Ext.form.TextArea({
                            value: '%s',
                            readOnly: true,
                        })
                    ],
                    buttons:[{
                        text:'Закрыть',
                        handler: function(){ msg_win.close() }
                    }]

                })
                msg_win.show();
            })()
            """ % (
                title, width, height,
                data.replace("\n", r"\n").replace(r"'", r'"'))
        )
    )
