# coding: utf-8
"""
Инструменарий для упрощённого создания ActionPack`ов для зависимых моделей
"""
from __future__ import absolute_import

from m3_django_compat import ModelOptions
from m3_django_compat import get_related

from objectpack.actions import ObjectPack


class SlavePack(ObjectPack):
    """
    "Ведомый" набор действий. Используется чаще всего для грида внутри
    окна редактирования объекта, отображающего объеты,
    связанные с редактируемым
    """
    # parents - список полей в модели которые должны браться из контекста
    # например: parents = ['employer', 'subject']
    parents = []

    __parents_cached = None

    @property
    def _parents(self):
        """
        Возвращает структуру вида:
        [
            (id_param_name род.пака, род.поле),
            ...
        ]
        """
        if self.__parents_cached:
            return self.__parents_cached
        opts = ModelOptions(self.model)
        result = self.__parents_cached = []
        for parent in self.parents:
            f = opts.get_field(parent)
            # pack ищется в реестре "модель-pack", который должен
            model = get_related(f).parent_model
            pack = self._get_model_pack(model.__name__)
            if pack:
                result.append((
                    pack.id_param_name,
                    parent
                ))
        return result

    def declare_context(self, action):
        """
        Возвращает декларацию контекста для экшна
        """
        result = super(SlavePack, self).declare_context(action)
        if action in (
            self.list_window_action,
            self.select_window_action,
            self.rows_action,
            self.edit_window_action,
            self.new_window_action,
            self.save_action
        ):
            # для экшнов декларируются id родителей
            for p in self._parents:
                result[p[0]] = {'type': 'int'}
        return result

    def _get_parents_dict(self, context, key_fmt='%s'):
        """
        Возвращает словарь из параметров контекста, представляющих родителей
        """
        return dict(
            (key_fmt % field_name, getattr(context, id_param_name))
            for id_param_name, field_name in self._parents
        )

    def save_row(self, obj, create_new, request, context):
        obj.__dict__.update(
            self._get_parents_dict(context, key_fmt='%s_id')
        )
        return super(SlavePack, self).save_row(
            obj, create_new, request, context)

    def get_rows_query(self, request, context):
        q = super(SlavePack, self).get_rows_query(request, context)
        return q.filter(**self._get_parents_dict(context))

    # SlavePack обычно не является основным для модели
    _is_primary_for_model = False
