from ievv_opensource import ievv_batchframework


class IndexAction(ievv_batchframework.Action):
    #: The :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` that this
    #: index action updates.
    doctype_class = None

    def execute(self):
        ids = self.kwargs['ids']
        self.logger.info('Indexing %s: %r', self.doctype_class.__name__, ids)
        self.doctype_class.indexupdater.bulk_index_model_ids(ids=ids)


def indexaction_factory(doctype_class, baseclass=None, name=None,):
    """

    Args:
        doctype_class: The :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` subclass.
        baseclass: The base class for the index action. Defaults to :class:`.IndexAction`.
        name: The name of the dynamically created :class:`.IndexAction` subclass. Defaults
            to ``<doctype_class.__name__>IndexAction``.

    Returns:
        IndexAction: A dyncamically created subclass of :class:`.IndexAction` with the
            :obj:`~.IndexAction.doctype_class` set to the provided ``doctype_class``.
    """
    if baseclass is None:
        baseclass = IndexAction
    if name is None:
        name = '{}IndexAction'.format(doctype_class.__name__)
    return type(name, (baseclass,), {'doctype_class': doctype_class})
