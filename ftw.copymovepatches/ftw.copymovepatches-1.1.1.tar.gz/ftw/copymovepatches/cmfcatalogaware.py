import inspect
from Acquisition import aq_base
from OFS.interfaces import IObjectWillBeMovedEvent
from plone import api
from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from ftw.copymovepatches.utils import HAS_C_INDEXING


"""This is the original method, we are replacing:
From https://github.com/zopefoundation/Products.CMFCore/blob/2.2.9/Products/CMFCore/CMFCatalogAware.py
Products.CMFCore 2.2.9


def handleContentishEvent(ob, event):

    if IObjectAddedEvent.providedBy(event):
        ob.notifyWorkflowCreated()
        ob.indexObject()

    elif IObjectMovedEvent.providedBy(event):
        if event.newParent is not None:
            ob.indexObject()

    elif IObjectWillBeMovedEvent.providedBy(event):
        if event.oldParent is not None:
            ob.unindexObject()

    elif IObjectCopiedEvent.providedBy(event):
        if hasattr(aq_base(ob), 'workflow_history'):
            del ob.workflow_history

    elif IObjectCreatedEvent.providedBy(event):
        if hasattr(aq_base(ob), 'addCreator'):
            ob.addCreator()

"""

"""
Basically it does not an uncatalog an afterwards a catalog, but just updates
the new path where necessary. This saves us from reindexing the whole moved
structure.
Unfortunately there are several path related indexes, which needs to be update.
But so far this change means a performance boost by factor 10.

The main issue was that the searchableText from Files was indexed again.

Messurements:
Folder with a Document and 300 simple PDF-Files:
OLD: about 80s
NEW: about 8s
"""


def handleContentishEvent(ob, event):
    """ Event subscriber for (IContentish, IObjectEvent) events.
    """
    if IObjectAddedEvent.providedBy(event):
        ob.notifyWorkflowCreated()
        ob.indexObject()

    elif IObjectMovedEvent.providedBy(event):
        if event.newParent is not None:
            if hasattr(aq_base(ob), 'notifyModified'):
                ob.notifyModified()

            rid = getattr(ob, '__rid', None)

            if rid:
                catalog = api.portal.get_tool('portal_catalog')
                _catalog = catalog._catalog

                new_path = '/'.join(ob.getPhysicalPath())
                old_path = _catalog.paths[rid]

                del _catalog.uids[old_path]
                _catalog.uids[new_path] = rid
                _catalog.paths[rid] = new_path

                ob.reindexObject(idxs=[
                    'path',
                    'allowedRolesAndUsers',
                    'modified',
                    'Date',
                    'id',
                    'getId'])

                delattr(ob, '__rid')
            elif event.newParent is not None:
                # This may happen if "collective.indexing" is installed and an object
                # is added and renamed/moved in the same transaction (e.g. during the
                # creation of an object with "plone.api" in a subscriber listening
                # on "IObjectAddedEvent" as in https://github.com/4teamwork/ftw.events/blob/f1a77440866c6d963961497f68781098c1b4bc8f/ftw/events/configure.zcml#L22).
                ob.indexObject()

    elif IObjectWillBeMovedEvent.providedBy(event):

        from ftw.copymovepatches.utils import getQueue

        # Prepare Rename if indexing queue is implemented
        if event.oldParent == event.newParent and getQueue is not None:
            # The queue needs to be processed, since the `renameObjectsByPaths`
            # script allows the user to rename the object and also sets a new
            # title if he wants.
            # In some circumstances this leads to a inconsistent catalog state.
            # Mainly if other event handler also triggers a `process` queue by
            # asking the catalog for something.
            # The result was for example a "reindex" of a already deleted
            # object.
            queue = getQueue()
            queue.process()

        # Move/Rename
        if event.oldParent is not None and event.newParent is not None:
            try:
                catalog = api.portal.get_tool('portal_catalog')
            except api.exc.CannotGetPortalError:
                # Happens when renaming a Plone Site in the ZMI.
                # Then it is best to manually clear and rebuild the catalog later anyway.
                # But for now do what would happen without our patch.
                ob.unindexObject()
            else:
                ob_path = '/'.join(ob.getPhysicalPath())
                if ob_path in catalog._catalog.uids:
                    rid = catalog._catalog.uids[ob_path]
                    setattr(ob, '__rid', rid)
                else:
                    # This may happen if "collective.indexing" is installed and an object
                    # is added and renamed/moved in the same transaction (e.g. during the
                    # creation of an object with "plone.api" in a subscriber listening
                    # on "IObjectAddedEvent" as in https://github.com/4teamwork/ftw.events/blob/f1a77440866c6d963961497f68781098c1b4bc8f/ftw/events/configure.zcml#L22).
                    return
        elif event.oldParent is not None:
            # Delete
            ob.unindexObject()

    elif IObjectCopiedEvent.providedBy(event):
        if hasattr(aq_base(ob), 'workflow_history'):
            del ob.workflow_history

    elif IObjectCreatedEvent.providedBy(event):
        if hasattr(aq_base(ob), 'addCreator'):
            ob.addCreator()


def marmoset_patch(old, new, extra_globals={}):
    g = old.func_globals
    g.update(extra_globals)
    c = inspect.getsource(new)
    exec c in g

    old.func_code = g[new.__name__].func_code


def apply_patch(scope, original, replacement):
    marmoset_patch(scope.handleContentishEvent,
                   replacement,
                   {'api': api,
                    'HAS_C_INDEXING': HAS_C_INDEXING})
