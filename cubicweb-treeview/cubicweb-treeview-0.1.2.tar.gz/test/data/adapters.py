from cubicweb_treeview.adapters import TVITreeAdapter
from cubicweb.predicates import is_instance


class NoteTreeViewAdapter(TVITreeAdapter):
    __select__ = is_instance('Note')
