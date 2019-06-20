# -*- coding: utf-8 -*-
from congo.conf import settings
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

def get_model(constant_name):
    """
    Zwraca model dla stałej zdefiniowanej w ``settings`` wyrażonej jako ścieżka ``app_name.ModelName``.
    
    .. code-block:: python
    
        # settings.CONGO_EMAIL_SENDER_MODEL = 'communication.EmailSender'
        
        def get_email_sender_model():
            return get_model('CONGO_EMAIL_SENDER_MODEL')
    """

    constant_value = getattr(settings, constant_name)

    try:
        return django_apps.get_model(constant_value)
    except AttributeError:
        raise ImproperlyConfigured("%s needs to be defined in settings as 'app_label.model_name'" % constant_name)
    except ValueError:
        raise ImproperlyConfigured("%s must be of the form 'app_label.model_name'" % constant_name)
    except LookupError:
        raise ImproperlyConfigured("%s refers to model '%s' that has not been installed" % (constant_name, constant_value))

class Iter(object):
    """
    Klasa pozwalająca na wydajne iterowanie po obiektach z querysetu. Wrzuca wszystko do pamięci,
    co przyspiesza operacje.
    
    .. code-block:: python
    
        iterator = Iter(Products.objects.all())
    """

    def __init__(self, queryset):
        """
        Tworzy iterator z obiektu ``queryset``.
        
        Użycie: ``foo_iter = Iter(Foo.objects.all())``
        """
        self.obj_dict = {}
        self.id_list = []
        for obj in queryset:
            self.id_list.append(obj.id)
            self.obj_dict[obj.id] = obj

    def __iter__(self):
        return iter(self.id_list)

    def __len__(self):
        return len(self.id_list)

    def _object_passes_test(self, attr, value, operator):
        if operator == 'eq':
            return attr == value
        elif operator == 'neq':
            return attr != value
        elif operator == 'gte':
            return attr >= value
        elif operator == 'gt':
            return attr > value
        elif operator == 'lte':
            return attr <= value
        elif operator == 'lt':
            return attr < value
        elif operator == 'in':
            return attr in value
        return False

    def get_object(self, obj_id):
        """
        Zwraca obiekt o wskazanym ID.
        """
        try:
            return self.obj_dict[int(obj_id)]
        except KeyError:
            return None

    def get_objects(self):
        """
        Zwraca listę wszystkich obiektów w kolejności, w jakiej były pobrane.
        """
        return [self.obj_dict[obj_id] for obj_id in self.id_list]

    def get_nested_objects(self, attr):
        """
        Zwraca listę zagnieżdżonych obiektów pod atrybutem o podanej nazwie.
        
        .. code-block:: python
        
            class Foo(models.Model):
                bar = models.ForeignKey(Bar)
    
            foo_iter = Iter(Foo.objects.all())
            foo_iter.get_nested_objects('bar')
            # [<Bar: bar1>, <Bar: bar2>, ...] 
        """
        result = []
        for obj_id in self.id_list:
            if hasattr(self.obj_dict[obj_id], attr):
                nested_obj = getattr(self.obj_dict[obj_id], attr)
                if nested_obj not in result:
                    result.append(nested_obj)
        return result

    def get_objects_by_id_list(self, id_list):
        id_list = map(lambda obj_id: int(obj_id), id_list)
        result = []
        for obj_id in filter(lambda obj_id: int(obj_id) in id_list, self.id_list):
            result.append(self.obj_dict[obj_id])

        return result

    def get_object_by_attr(self, attr, value, operator = 'eq'):
        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            if hasattr(obj, attr):
                if self._object_passes_test(getattr(obj, attr), value, operator):
                    return obj
        return None

    def get_object_by_attrs(self, attrs):
        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            valid = True
            for attr_dict in attrs:
                attr = attr_dict['attr']
                value = attr_dict['value']
                operator = attr_dict.get('operator', 'eq')

                if hasattr(obj, attr):
                    if not self._object_passes_test(getattr(obj, attr), value, operator):
                        valid = False
                else:
                    valid = False
            if valid:
                return obj
        return None

    def get_objects_by_attr(self, attr, value, operator = "eq"):
        result = []

        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            if hasattr(obj, attr):
                if self._object_passes_test(getattr(obj, attr), value, operator):
                    result.append(obj)
        return result

    def get_objects_by_attrs(self, attrs):
        result = []

        for obj_id in self.id_list:
            obj = self.obj_dict[obj_id]

            valid = True
            for attr_dict in attrs:
                attr = attr_dict['attr']
                value = attr_dict['value']
                operator = attr_dict.get('operator', 'eq')

                if hasattr(obj, attr):
                    if not self._object_passes_test(getattr(obj, attr), value, operator):
                        valid = False
                else:
                    valid = False
            if valid:
                result.append(obj)
        return result

    def get_next(self, obj_id):
        try:
            return self.obj_dict[self.id_list[self.id_list.index(int(obj_id)) + 1]]
        except IndexError:
            return None

    def get_prev(self, obj_id):
        try:
            prev_id = self.id_list.index(int(obj_id)) - 1
            if prev_id >= 0:
                return self.obj_dict[self.id_list[prev_id]]
            else:
                return None
        except IndexError:
            return None

    def get_previous(self, obj_id):
        return self.get_prev(obj_id)

    def get_index(self, obj_id, count_from_1 = False):
        index = self.id_list.index(int(obj_id))
        return index + 1 if count_from_1 else index

class Tree(Iter):
    def __init__(self, query):
        self.obj_dict = {}
        self.id_list = []
        self.root_id_list = []
        self.child_id_dict = {}
        for obj in query:
            self.id_list.append(obj.id)
            self.obj_dict[obj.id] = obj
            if obj.parent_id:
                if obj.parent_id in self.child_id_dict:
                    self.child_id_dict[obj.parent_id].append(obj.id)
                else:
                    self.child_id_dict[obj.parent_id] = [obj.id]
            else:
                self.root_id_list.append(obj.id)

    def get_root(self, obj_id, get_self = False):
        obj = self.get_object(obj_id)
        if not obj:
            return None
        while obj.parent_id:
            obj = self.get_parent(obj.id)
        if obj.id != int(obj_id) or get_self:
            return obj
        else:
            return None

    def get_roots(self):
        return self.get_objects_by_id_list(self.root_id_list)

    def get_parent(self, obj_id, get_self = False):
        obj = self.get_object(obj_id)
        if not obj:
            return None
        if obj.parent_id:
            return self.get_object(obj.parent_id)
        else:
            if get_self:
                return obj
            else:
                return None

    def get_ancestors(self, obj_id, ascending = False, include_self = False):
        """
        Zwraca listę przodków (rodziców) obiektu o podanym ID; domyślnie od najstarszego (korzenia) do najmłodszego (bezpośredniego rodzica).
        """
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result

        if include_self:
            result.append(obj)

        while obj.parent_id:
            obj = self.get_parent(obj.id)
            if obj:
                result.append(obj)
            else:
                break

        if not ascending:
            result.reverse()

        return result

    def get_parents(self, obj_id, get_self = False, reverse = True):
        warn(u"This method is deprecated. Use 'get_ancestors' instead.", DeprecationWarning)

        return self.get_ancestors(obj_id, ascending = not reverse, include_self = get_self)

    def get_children(self, obj_id, include_self = False, **kwargs):
        """
        Zwraca listę bezpośrednich przodków (dzieci).
        """
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result

        if 'get_self' in kwargs:
            warn(u"Attribute 'get_self' is deprecated. Use 'include_self' instead.", DeprecationWarning)
            include_self = kwargs['get_self']

        if 'get_nested' in kwargs:
            warn(u"Attribute 'get_nested' is deprecated. Use 'get_descendants' method instead.", DeprecationWarning)
            self.get_descendants(obj_id, include_self)

        if include_self:
            result.append(obj)

        if obj.id in self.child_id_dict:
                result += self.get_objects_by_id_list(self.child_id_dict[obj.id])
        return result

    def get_descendants(self, obj_id, include_self = False):
        """
        Zwraca listę wszystkich potomków (dzieci) w kolejności drzewa.
        """
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result

        if include_self:
            result.append(obj)

        if obj.id in self.child_id_dict:
            for child_id in self.child_id_dict[obj.id]:
                result.append(self.get_object(child_id))
                result += self.get_descendants(child_id)

        return result

    def get_family(self, obj_id):
        """
        Zwraca listę przodków (rodziców), obiekt o podanym ID oraz wszystkich przodków w kolejności drzewa.
        """
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result

        result += self.get_ancestors(obj_id)
        result += self.get_descendants(obj_id, include_self = True)
        return result

    def get_siblings(self, obj_id, include_self = False, **kwargs):
        obj = self.get_object(obj_id)
        result = []

        if not obj:
            return result

        if 'get_self' in kwargs:
            warn(u"Attribute 'get_self' is deprecated. Use 'include_self' instead.", DeprecationWarning)
            include_self = kwargs['get_self']

        if obj.parent_id:
            result += filter(lambda x: x != obj or include_self, self.get_children(obj.parent_id))
        else:
            result += filter(lambda x: x != obj or include_self, self.get_roots())
        return result

    def get_next_sibling(self, obj_id):
        obj = self.get_object(obj_id)
        result = None

        if not obj:
            return result

        if obj.parent_id:
            siblings_id_list = self.child_id_dict[obj.parent_id]
        else:
            siblings_id_list = self.root_id_list

        try:
            index = siblings_id_list.index(int(obj_id))
            result = self.get_object(siblings_id_list[index + 1])
        except (ValueError, IndexError):
            result = None

        return result

    def get_prev_sibling(self, obj_id):
        obj = self.get_object(obj_id)
        result = None

        if not obj:
            return result

        if obj.parent_id:
            siblings_id_list = self.child_id_dict[obj.parent_id]
        else:
            siblings_id_list = self.root_id_list

        try:
            index = siblings_id_list.index(int(obj_id))
            result = self.get_object(siblings_id_list[index - 1]) if index > 0 else None
        except (ValueError, IndexError):
            result = None

        return result

    def get_previous_sibling(self, obj_id):
        return self.get_prev(obj_id)

    def has_parent(self, obj_id):
        obj = self.get_object(obj_id)
        if not obj:
            return False
        return bool(obj.parent_id)

    def has_children(self, obj_id):
        return obj_id in self.child_id_dict

    def has_siblings(self, obj_id):
        return bool(len(self.get_siblings(obj_id)))

    def has_next_sibling(self, obj_id):
        return bool(self.get_next_sibling(obj_id))

    def has_prev_sibling(self, obj_id):
        return bool(self.get_prev_sibling(obj_id))

    def has_previous_sibling(self, obj_id):
        return self.has_prev_sibling(obj_id)

    def is_child_node(self, obj_id):
        """
        Sprawdza, czy obiekt ma rodzica.
        
        *Dla utrzymania kompatybilności z metodami django-mtpp.*
        """
        return self.has_parent(obj_id)

    def is_leaf_node(self, obj_id):
        """
        Sprawdza, czy obiekt jest liściem (nie ma dzieci).
        
        *Dla utrzymania kompatybilności z metodami django-mtpp.*
        """
        return not self.has_children(obj_id)

    def is_root_node(self, obj_id):
        """
        Sprawdza, czy obiekt jest korzeniem (nie ma rodzica).
        
        *Dla utrzymania kompatybilności z metodami django-mtpp.*
        """
        return not self.has_parent(obj_id)

    def to_json(self, attrs = [], evals = {}):
        """
        Zwraca drzewo w json w oparciu o podane attrs (id jest domyslne) i slownik evals.
        
        Użycie::
            tree_obj.to_json(attrs = ['name'], evals = {'url': 'get_absolute_url(mode = "news")'})
        """

        if not 'id' in attrs:
            attrs.append('id')

        def build_json_obj(tree, obj, attrs, evals):
            json_obj = {}

            # set json_obj attrs
            for attr in attrs:
                json_obj[attr] = getattr(obj, attr)

            # set json_obj evals
            for k, v in evals.items():
                try:
                    e = eval("obj.%s" % v)
                except TypeError:
                    e = "Function does not exist!"
                json_obj[k] = e

            # build children recursive
            children = tree.get_children(json_obj.get('id'))
            if children:
                json_children = []

                for child in children:
                    json_children.append(build_json_obj(tree, child, attrs, evals))

                json_obj['children'] = json_children

            return json_obj

        # build json tree
        json_tree = []

        for obj in self.get_roots():
            json_tree.append(build_json_obj(self, obj, attrs, evals))

        return json_tree
