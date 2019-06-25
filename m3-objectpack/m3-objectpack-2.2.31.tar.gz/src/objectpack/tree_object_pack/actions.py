# coding: utf-8
u"""Действия для работы с древовидными справочниками."""
from __future__ import absolute_import

from collections import OrderedDict

from m3 import actions as m3_actions
from m3_django_compat import get_request_params

from objectpack.actions import ObjectPack
from objectpack.actions import ObjectRowsAction
from objectpack.tools import extract_int
from objectpack.tools import int_or_none

from . import ui


class TreeObjectPack(ObjectPack):
    u"""Пак для работы с моделями древовидной иерархии."""
    parent_field = 'parent'
    u"""Поле модели - ссылка на родителя."""

    list_window = ui.BaseTreeListWindow
    select_window = ui.BaseTreeSelectWindow

    load_trees_on_search = False
    u"""Флаг загрузки полной иерархии при поиске.

    True - при поиске отображаются полные пути до найденных записей,
    False - при поиске отображаются только найденные записи.
    """

    def __init__(self, *args, **kwargs):
        super(TreeObjectPack, self).__init__(*args, **kwargs)
        self.replace_action('rows_action', TreeObjectRowsAction())
        self.autocomplete_action = ObjectRowsAction()
        self.actions.append(self.autocomplete_action)

    def apply_search(self, query, request, context):
        u"""Поиск применяется только на корневом узле.

        :param query: QuerySet для поиска.
        :type query: django.db.models.query.QuerySet
        :type request: django.http.HttpRequest
        :type context: m3.actions.context.DeclarativeActionContext
        :return: Отфильтрованный QuerySet.
        :rtype: django.db.models.query.QuerySet
        """
        id_param_name = extract_int(request, self.id_param_name)
        if id_param_name and id_param_name > 0:
            return query

        return super(
            TreeObjectPack, self).apply_search(query, request, context)

    def get_rows_query(self, request, context):
        u"""Получение записей в зависимости текущего узла и поиска."""
        result = super(TreeObjectPack, self).get_rows_query(request, context)
        # данные подгружаются "поуровнево", для чего
        # запрос содержит id узла, из которого поддерево "растет"
        current_node_id = extract_int(request, self.id_param_name)
        filter_in_params = bool(get_request_params(request).get('filter'))
        # при применении поиска на корневом узле, берутся все записи
        if filter_in_params and current_node_id < 0:
            return result

        if current_node_id < 0:
            # если корневой узел поддерева не указан, будут выводиться
            # деревья самого верхнего уровня (не имеющие родителей)
            current_node_id = None

        result = result.filter(
            **{('%s__id' % self.parent_field): current_node_id})

        return result

    def configure_grid(self, grid):
        super(TreeObjectPack, self).configure_grid(grid)
        grid.action_data = self.rows_action
        if not self.read_only:
            grid.action_new = self.new_window_action
            grid.action_edit = self.edit_window_action
            grid.action_delete = self.delete_action

    def create_edit_window(self, create_new, request, context):
        win = super(TreeObjectPack, self).create_edit_window(
            create_new, request, context)
        parent_id = getattr(context, 'parent_id', None)
        if context.parent_id is not None:
            win.form.from_object({'parent_id': parent_id})
        return win

    def save_row(self, obj, create_new, request, context):
        parent_id = getattr(context, 'parent_id', None)
        setattr(obj, '%s_id' % self.parent_field, parent_id)
        obj.save()

    def declare_context(self, action):
        decl = super(TreeObjectPack, self).declare_context(action)
        if action is self.new_window_action:
            decl[self.id_param_name]['default'] = 0
        if action in (
            self.edit_window_action,
            self.new_window_action,
            self.save_action
        ):
            # id может и не прийти,
            # если добавление производится в корень
            decl['parent_id'] = {'type': int_or_none, 'default': None}
        return decl

    def get_autocomplete_url(self):
        return self.autocomplete_action.get_absolute_url()


class TreeObjectRowsAction(ObjectRowsAction):
    u"""Экшн для получения данных древовидной модели."""

    def _create_trees(self):
        u"""Создание деревьев при поиске.

        Мерж веток всех найденных записей в один словарь.

        :return: Словарь деревьев.
        :rtype: collections.OrderedDict
        """

        trees = OrderedDict()

        for obj in self.query:
            # Получение ветки
            branch = obj.get_ancestors(include_self=True)

            if not branch:
                self.query.skip_last()
                continue

            def create_node(obj_):
                """Узел в dict представлении."""
                return dict(obj=obj_, children={})

            root = branch[0]
            # Создается корневой узел, если не создан
            trees.setdefault(root.id, create_node(root))
            dict_node = trees[root.id]
            # Преобразование ветки в dict
            for node in branch[1:]:
                dict_node['children'].setdefault(node.id, create_node(node))
                dict_node = dict_node['children'][node.id]

        return trees

    def get_rows(self):
        u"""Метод производит преобразование QuerySet в список.

        При поиске возвращаются деревья с потомками.

        :return: Список сериализованных объектов
        :rtype: list
        """
        if (
            not self.parent.load_trees_on_search or
            not get_request_params(self.request).get('filter') or
            extract_int(self.request, self.parent.id_param_name) > 0
        ):
            return super(TreeObjectRowsAction, self).get_rows()

        trees = self._create_trees()

        def prepare_node(node):
            u"""Преобразовывает узел и потомков в результирующий список.

            :param node: Узел дерева.
            :type node: mptt.models.MPTTModel
            """
            rv = self.prepare_object(node['obj'])

            for child in node['children'].values():
                rv.setdefault('children', []).append(prepare_node(child))

            return rv

        result = []

        for node in trees.values():
            result.append(prepare_node(node))

        return self.handle('get_rows', result)

    def _is_leaf(self, obj):
        u"""Получение состояния вложенности объкта.

        :param obj: Объект, полученный из QuerySet'a.
        :type obj: django.db.models.Model
        :return: Имеет ли объект вложенные объекты.
        :rtype: bool
        """
        if hasattr(self.parent.model, 'is_leaf'):
            # модель может сама предоставлять признак "лист"/"не лист"
            is_leaf = obj.is_leaf
        elif hasattr(self.parent.model, 'is_leaf_node'):
            # метод для :class:`mptt.models.MPTTModel` модели
            is_leaf = obj.is_leaf_node()
        else:
            # для моделей, не предоставляющих информацию о ветвлении,
            # формируется предикат на основе связей узлов дерева
            key = self.parent.parent_field
            parents = self.parent.model.objects.filter(**{
                ('%s__isnull' % key): False,
            }).values_list(
                '%s__id' % key,
                flat=True
            )
            is_leaf = obj.id not in parents

        return is_leaf

    def prepare_object(self, obj):
        u"""Сериализация объекта в словарь.

        К сериализованному объекту добавляется атрибут наличия вложенности.

        :param obj: Объект, полученный из QuerySet'a.
        :type obj: django.db.models.Model
        :return: Словарь для сериализации в JSON.
        :rtype: dict
        """
        data = super(TreeObjectRowsAction, self).prepare_object(obj)
        data['leaf'] = self._is_leaf(obj)

        return data

    def run(self, *args, **kwargs):
        u"""Возвращает JSON список объектов."""
        result = super(TreeObjectRowsAction, self).run(*args, **kwargs)
        data = result.data.get('rows', [])

        return m3_actions.PreJsonResult(data)
