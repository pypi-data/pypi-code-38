# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Acquisition import aq_base
from appy.gen import No
from imio.actionspanel import ActionsPanelMessageFactory as _
from imio.actionspanel.interfaces import IContentDeletable
from imio.actionspanel.utils import findViewableURL
from imio.actionspanel.utils import unrestrictedRemoveGivenObject
from imio.history.interfaces import IImioHistory
from operator import itemgetter
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.ActionInformation import ActionInfo
from Products.CMFCore.permissions import ManageProperties
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone import PloneMessageFactory as _plone
from Products.CMFPlone.utils import safe_unicode
from Products.DCWorkflow.Expression import createExprContext
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate

import json
import transaction


DEFAULT_CONFIRM_VIEW = '@@triggertransition'


class ActionsPanelView(BrowserView):
    """
      This manage the view displaying actions on context.
    """
    def __init__(self, context, request):
        super(ActionsPanelView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.parent = self.context.getParentNode()
        self.member = self.request.get('imio.actionspanel_member_cachekey', None)
        if not self.member:
            self.member = api.user.get_current()
            self.request.set('imio.actionspanel_member_cachekey', self.member)
        self.portal_url = self.request.get('imio.actionspanel_portal_url_cachekey', None)
        self.portal = self.request.get('imio.actionspanel_portal_cachekey', None)
        if not self.portal_url or not self.portal:
            self.portal = api.portal.get()
            self.portal_url = self.portal.absolute_url()
            self.request.set('imio.actionspanel_portal_url_cachekey', self.portal_url)
            self.request.set('imio.actionspanel_portal_cachekey', self.portal)
        self.SECTIONS_TO_RENDER = ('renderTransitions',
                                   'renderEdit',
                                   'renderExtEdit',
                                   'renderOwnDelete',
                                   'renderArrows',
                                   'renderActions',
                                   'renderAddContent',
                                   'renderHistory')
        # portal_actions.object_buttons action ids not to keep
        # every actions will be kept except actions listed here
        self.IGNORABLE_ACTIONS = ()

        # portal_actions.object_buttons action ids to keep
        # if you define some here, only these actions will be kept
        self.ACCEPTABLE_ACTIONS = ()

    def __call__(self,
                 useIcons=True,
                 showTransitions=True,
                 appendTypeNameToTransitionLabel=False,
                 showEdit=True,
                 showExtEdit=False,
                 showOwnDelete=True,
                 showActions=True,
                 showAddContent=False,
                 showHistory=False,
                 showHistoryLastEventHasComments=True,
                 showArrows=False,
                 arrowsPortalTypeAware=False,
                 **kwargs):
        """
          Master method that will render the content.
          This is not supposed to be overrided.
        """
        self.useIcons = useIcons
        self.showTransitions = showTransitions
        self.appendTypeNameToTransitionLabel = appendTypeNameToTransitionLabel
        self.showEdit = showEdit
        self.showExtEdit = showExtEdit
        self.showOwnDelete = showOwnDelete
        # if 'delete' is in acceptable actions, it takes precedence on showOwnDelete
        if showActions and 'delete' in self.ACCEPTABLE_ACTIONS:
            self.showOwnDelete = False
        # if we manage our own delete, do not use Plone default one
        elif self.showOwnDelete and 'delete' not in self.IGNORABLE_ACTIONS:
            self.IGNORABLE_ACTIONS = self.IGNORABLE_ACTIONS + ('delete', )
        self.showActions = showActions
        self.showAddContent = showAddContent
        self.showHistory = showHistory
        self.showHistoryLastEventHasComments = showHistoryLastEventHasComments
        self.showArrows = showArrows
        # arrowsPortalTypeAware will change the script used to
        # change object position.  It is used when several elements of
        # various portal_type are in the same container but we want to
        # order the elements of same portal_type together
        self.arrowsPortalTypeAware = arrowsPortalTypeAware
        self.kwargs = kwargs
        self.hasActions = False
        return self.index()

    def isInFacetedNavigation(self):
        """Is the actions panel displayed in a faceted navigation?"""
        return bool(self.request['URL'].endswith('@@faceted_query'))

    def _renderSections(self):
        """
          This will check what sections need to be rendered.
          This is not supposed to be overrided.
        """
        res = ''

        for section in self.SECTIONS_TO_RENDER:
            renderedSection = getattr(self, section)() or ''
            res += renderedSection
        return res

    def renderArrows(self):
        """
          Render arrows if user may change order of elements.
        """
        if not self.useIcons:
            return ''

        if self.showArrows and self.member.has_permission(ManageProperties, self.parent):
            self.parentObjectIds = [
                ob.id for ob in self.parent.objectValues()
                if (not self.arrowsPortalTypeAware or ob.portal_type == self.context.portal_type)]
            self.objId = self.context.getId()
            self.moveUrl = self._moveUrl()
            return ViewPageTemplateFile("actions_panel_arrows.pt")(self)
        return ''

    def _moveUrl(self):
        """ """
        script_name = 'folder_position'
        if self.arrowsPortalTypeAware:
            script_name = 'folder_position_typeaware'

        return "{0}/{1}?position=%s&id=%s&template_id={2}".format(
            self.parent.absolute_url(), script_name, self._returnTo())

    def _returnTo(self, ):
        """What URL should I return to after moving the element and page is refreshed."""
        return self.request.getURL()

    def renderTransitions(self):
        """
          Render the current context available workflow transitions.
        """
        if self.showTransitions:
            return ViewPageTemplateFile("actions_panel_transitions.pt")(self)
        return ''

    def renderEdit(self):
        """
          Render a 'edit' action.  By default, only available when actions are displayed
          as icons because when it is not the case, we already have a 'edit' tab and that would
          be redundant.
        """
        if self.showEdit and self.useIcons and self.mayEdit():
            return ViewPageTemplateFile("actions_panel_edit.pt")(self)
        return ''

    def renderExtEdit(self):
        """
          Render a 'external_edit' action.  By default, only available when actions are displayed
          as icons because when it is not the case, we already have a 'external_edit' viewlet and that would
          be redundant.
        """
        if self.showExtEdit and self.useIcons and self.mayExtEdit():
            return ViewPageTemplateFile("actions_panel_ext_edit.pt")(self)
        return ''

    def renderOwnDelete(self):
        """
          Render our own version of the 'delete' action.
        """
        if self.showOwnDelete and \
           IContentDeletable(self.context).mayDelete():
            return ViewPageTemplateFile("actions_panel_own_delete.pt")(self)
        return ''

    def renderActions(self):
        """
          Render actions coming from portal_actions.object_buttons and available on the context.
        """
        if self.showActions:
            return ViewPageTemplateFile("actions_panel_actions.pt")(self)

    def renderAddContent(self):
        """
          Render allowed_content_types coming from portal_type.
        """
        if self.showAddContent:
            return ViewPageTemplateFile("actions_panel_add_content.pt")(self)

    def renderHistory(self):
        """
          Render a link to the object's history (@@historyview).
        """
        if self.showHistory and self.useIcons and self.showHistoryForContext():
            return ViewPageTemplateFile("actions_panel_history.pt")(self)

    def showHistoryForContext(self):
        """
          Method to control access to the @@historyview view and so to the action icon.
          We rely on view 'contenthistory' overrided in imio.history.
        """
        contenthistory = getMultiAdapter((self.context, self.request), name='contenthistory')
        return contenthistory.show_history()

    def historyLastEventHasComments(self):
        """
          Returns True if the last event of the object's history has a comment.
        """
        adapter = getAdapter(self.context, IImioHistory, 'workflow')
        return adapter.historyLastEventHasComments()

    def mayEdit(self):
        """
          Method that check if special 'edit' action has to be displayed.
        """
        return self.member.has_permission('Modify portal content', self.context)

    def mayExtEdit(self):
        """
          Method that check if special 'external_edit' action has to be displayed.
        """
        if not self.member.has_permission('Modify portal content', self.context):
            return False
        portal_quickinstaller = api.portal.get_tool('portal_quickinstaller')
        external_edit_installed = portal_quickinstaller.isProductInstalled('collective.externaleditor')
        if not external_edit_installed:
            return False
        # Can be to slow for a dashboard ?
        # view = getMultiAdapter((self.context, self.request), name='externalEditorEnabled')
        # return view.available()
        # The availability check can be simpler because external_edit view check also availability
        # with available method
        registry = getUtility(IRegistry)
        # check if enabled
        if not registry.get('externaleditor.ext_editor', False):
            return False
        # check portal type
        externaleditor_enabled_types = registry.get('externaleditor.externaleditor_enabled_types', [])
        return self.context.portal_type in externaleditor_enabled_types

    def saveHasActions(self):
        """
          Save the fact that we have actions.
        """
        self.hasActions = True

    def sortTransitions(self, lst):
        """ Sort the list of transitions by title """
        lst.sort(key=itemgetter('title'))

    def getTransitions(self):
        """
          This method is similar to portal_workflow.getTransitionsFor, but
          with some improvements:
          - we retrieve transitions that the user can't trigger, but for
            which he needs to know for what reason he can't trigger it;
          - for every transition, we know if we need to display a confirm
            popup or not.
        """
        res = []
        # Get the workflow definition for p_obj.
        workflow = self.request.get('imio.actionspanel_workflow_%s_cachekey' % self.context.portal_type, None)
        if not workflow:
            wfTool = api.portal.get_tool('portal_workflow')
            workflows = wfTool.getWorkflowsFor(self.context)
            if not workflows:
                return res
            workflow = workflows[0]
            self.request.set('imio.actionspanel_workflow_%s_cachekey' % self.context.portal_type, workflow)
        # What is the current state for self.context?
        currentState = workflow._getWorkflowStateOf(self.context)
        if not currentState:
            return res
        # Get the transitions to confirm from the config.
        toConfirm = self._transitionsToConfirmInfos()
        # Analyse all the transitions that start from this state.
        for transitionId in currentState.transitions:
            transition = workflow.transitions.get(transitionId, None)
            if transition and (transition.trigger_type == TRIGGER_USER_ACTION) \
               and transition.actbox_name:
                # We have a possible candidate for a user-triggerable transition
                if transition.guard is None:
                    mayTrigger = True
                else:
                    mayTrigger = self._checkTransitionGuard(transition.guard,
                                                            self.member,
                                                            workflow,
                                                            self.context)
                if mayTrigger or isinstance(mayTrigger, No):
                    # Information about this transition must be part of result.
                    # check if the transition have to be confirmed regarding
                    # current object meta_type/portal_type and transition to trigger
                    preNameMetaType = '%s.%s' % (self.context.meta_type, transition.id)
                    preNamePortalType = '%s.%s' % (self.context.portal_type, transition.id)
                    confirmation_view = toConfirm.get(preNameMetaType, '') or toConfirm.get(preNamePortalType, '')
                    tInfo = {
                        'id': transition.id,
                        # if the transition.id is not translated, use translated transition.title...
                        'title': translate(safe_unicode(transition.title),
                                           domain="plone",
                                           context=self.request),
                        'description': transition.description,
                        'name': transition.actbox_name, 'may_trigger': True,
                        'confirm': bool(confirmation_view),
                        'confirmation_view': confirmation_view or DEFAULT_CONFIRM_VIEW,
                        'url': transition.actbox_url %
                            {'content_url': self.context.absolute_url(),
                             'portal_url': '',
                             'folder_url': ''},
                        'icon': transition.actbox_icon %
                            {'content_url': self.context.absolute_url(),
                             'portal_url': self.portal_url,
                             'folder_url': ''},
                    }
                    if not mayTrigger:
                        tInfo['may_trigger'] = False
                        # mayTrigger.msg is a 'zope.i18nmessageid.message.Message', translate it now
                        tInfo['reason'] = translate(mayTrigger.msg, context=self.request)
                    res.append(tInfo)

        self.sortTransitions(res)
        return res

    def _transitionsToConfirmInfos(self):
        transitions = self._transitionsToConfirm()
        if type(transitions) is not dict:
            transitions = dict([(t, DEFAULT_CONFIRM_VIEW) for t in transitions])
        else:
            for name, confirm_view in transitions.iteritems():
                if not confirm_view:
                    transitions[name] = DEFAULT_CONFIRM_VIEW
        return transitions

    def _transitionsToConfirm(self):
        """
          Return the list of transitions the user will have to confirm, aka
          the user will be able to enter a comment for.
          This is a per meta_type or portal_type list of transitions to confirm.
          So for example, this could be :
          ('ATDocument.reject', 'Document.publish', 'Collection.publish', )
          --> ATDocument is a meta_type and Document is a portal_type for example
          The list can also be a dict with the key being the transition name to
          confirm and the value being the name of the view to call to confirm
          the transition. eg:
          {'Document.reject': 'simpleconfirmview', 'Mytype.cancel': 'messageconfirmview'}
          If no confirmation view is provided (empty string) imio.actionspanel confirmation
          default view is used instead.
        """
        values = api.portal.get_registry_record(
            'imio.actionspanel.browser.registry.IImioActionsPanelConfig.transitions')
        if values is None:
            return ()
        return dict([val.split('|') for val in values])

    def _checkTransitionGuard(self, guard, sm, wf_def, ob):
        """
          This method is similar to DCWorkflow.Guard.check, but allows to
          retrieve the truth value as a appy.gen.No instance, not simply "1"
          or "0".
        """
        u_roles = None
        if wf_def.manager_bypass:
            # Possibly bypass.
            u_roles = sm.getRolesInContext(ob)
            if 'Manager' in u_roles:
                return 1
        if guard.permissions:
            for p in guard.permissions:
                if _checkPermission(p, ob):
                    break
            else:
                return 0
        if guard.roles:
            # Require at least one of the given roles.
            if u_roles is None:
                u_roles = sm.getRolesInContext(ob)
            for role in guard.roles:
                if role in u_roles:
                    break
            else:
                return 0
        if guard.groups:
            # Require at least one of the specified groups.
            u = sm.getUser()
            b = aq_base(u)
            if hasattr(b, 'getGroupsInContext'):
                u_groups = u.getGroupsInContext(ob)
            elif hasattr(b, 'getGroups'):
                u_groups = u.getGroups()
            else:
                u_groups = ()
            for group in guard.groups:
                if group in u_groups:
                    break
            else:
                return 0
        expr = guard.expr
        if expr is not None:
            econtext = createExprContext(StateChangeInfo(ob, wf_def))
            res = expr(econtext)
            return res
        return 1

    def getTransitionTitle(self, transition):
        '''Render the transition title including portal_type title if necessary.'''
        transition_title = transition['title']
        if self.appendTypeNameToTransitionLabel:
            typesTool = api.portal.get_tool('portal_types')
            type_info = typesTool.getTypeInfo(self.context)
            transition_title = u"{0} {1}".format(safe_unicode(transition_title),
                                                 translate(type_info.title,
                                                           domain=type_info.i18n_domain,
                                                           context=self.request))
        return transition_title

    def computeTriggerTransitionLink(self, transition):
        """ """
        return "{0}/{1}?transition={2}&actionspanel_view_name={3}{4}".format(
            self.context.absolute_url(),
            transition['confirmation_view'],
            transition['id'],
            self.__name__,
            not transition['confirm'] and '&form.submitted=1' or '')

    def computeTriggerTransitionOnClick(self, transition):
        """ """
        transition_ids = [tr['id'] for tr in self.getTransitions()]
        # if transition is no more available, this means that element's transition
        # was already triggered by another user or in another tab, we just refresh the page
        if not transition or transition['id'] not in transition_ids:
            return 'window.location.href=window.location.href;'
        if not transition['confirm']:
            return "triggerTransition(baseUrl='{0}', viewName='@@triggertransition', transition='{1}', this);".format(
                self.context.absolute_url(),
                transition['id'])
        else:
            return ''

    def computeDeleteGivenUIDOnClick(self):
        """ """
        return "deleteElement(baseUrl='{0}', viewName='@@delete_givenuid', object_uid='{1}');".format(
            self.context.absolute_url(),
            self.context.UID())

    def addableContents(self):
        """
          Return addable content types.
        """
        if not self.context.isPrincipiaFolderish:
            return []
        factories_view = getMultiAdapter((self.context, self.request),
                                         name='folder_factories')
        return factories_view.addable_types()

    def listObjectButtonsActions(self):
        """
          Return a list of object_buttons actions coming from portal_actions/portal_types.
        """
        actionsTool = api.portal.get_tool('portal_actions')
        typesTool = api.portal.get_tool('portal_types')
        # filter acceptable/ignorable actions before evaluating the TAL expression
        actions = [act for act in (actionsTool.listActions(categories=['object_buttons']) +
                                   tuple(typesTool.listActions(object=self.context, category='object_buttons')))
                   if (self.ACCEPTABLE_ACTIONS and act.id in self.ACCEPTABLE_ACTIONS) or
                      (not self.ACCEPTABLE_ACTIONS and act.id not in self.IGNORABLE_ACTIONS)]
        ec = actionsTool._getExprContext(self.context)
        actions = [ActionInfo(action, ec) for action in actions]
        objectButtonActions = [act for act in actions if act['visible'] and act['allowed'] and act['available']]

        res = []
        for action in objectButtonActions:
            act = action.copy()
            # We try to append the url of the icon of the action
            # look on the action itself
            if act['icon']:
                # make sure we only have the action icon name not a complete
                # path including portal_url or so, just take care that we do not have
                # an image in a static resource folder
                splittedIconPath = act['icon'].split('/')
                if len(splittedIconPath) > 1 and '++resource++' in splittedIconPath[-2]:
                    # keep last 2 parts of the path
                    act['icon'] = '/'.join((splittedIconPath[-2], splittedIconPath[-1], ))
                else:
                    act['icon'] = splittedIconPath[-1]
            res.append(act)
        return res

    def triggerTransition(self, transition, comment, redirect=True):
        """
          Triggers a p_transition on self.context.
        """
        wfTool = api.portal.get_tool('portal_workflow')
        plone_utils = api.portal.get_tool('plone_utils')
        try:
            wfTool.doActionFor(self.context,
                               transition,
                               comment=comment)
        except Exception, exc:
            # abort because element state was changed
            transaction.abort()
            plone_utils.addPortalMessage(exc.message, type='warning')
            return

        # use transition title to translate so if several transitions have the same title,
        # we manage only one translation
        transition_title = wfTool.getWorkflowsFor(self.context)[0].transitions[transition].title or \
            transition
        # add a portal message, we try to translate a specific one or add 'Item state changed.' as default
        msg = _(u'%s_done_descr' % safe_unicode(transition_title),
                default=_plone("Item state changed."))
        plone_utils.addPortalMessage(msg)

        http_referer = self.request.get('HTTP_REFERER')
        # After having triggered a wfchange, it the current user
        # can not access the obj anymore, try to find a place viewable by the user
        redirectToUrl = self._redirectToViewableUrl()
        if redirectToUrl != http_referer:
            return redirectToUrl
        else:
            # in some cases, redirection is managed at another level, by jQuery for example
            if not redirect:
                return
            return http_referer

    def _redirectToViewableUrl(self):
        """
          Return a url the user may access.
          This is called when user does not have access anymore to
          the object he triggered a transition for.
          First check if HTTP_REFERER is not the object not accessible, if it is not, we redirect
          to HTTP_REFERER, but if it is, we check parents until we find a viewable parent.
        """
        return findViewableURL(self.context, self.request, self.member)


class DeleteGivenUidView(BrowserView):
    """
      View that ease deletion of elements by not checking the 'Delete objects' permission on parent
      but only on the object to delete itself (default implentation of IContentDeletable.mayDelete).
      Callable using self.portal.restrictedTraverse('@@delete_givenuid)(object_to_delete.UID()) in the code
      and using classic traverse in a url : http://nohost/plonesite/delete_givenuid?object_uid=anUID
    """
    def __init__(self, context, request):
        super(DeleteGivenUidView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = api.portal.get()

    def __call__(self,
                 object_uid,
                 redirect=True,
                 catch_before_delete_exception=True):
        """ """
        # redirect can by passed by jQuery, in this case, we receive '0' or '1'
        if redirect == '0':
            redirect = False
        elif redirect == '1':
            redirect = True
        # Get the object to delete
        # try to get it from the portal_catalog
        catalog_brains = self.context.portal_catalog(UID=object_uid)
        # if not found, try to get it from the uid_catalog
        if not catalog_brains:
            catalog_brains = self.context.uid_catalog(UID=object_uid)
        # if nto found at all, raise
        if not catalog_brains:
            raise KeyError('The given uid could not be found!')
        obj = catalog_brains[0].getObject()

        # we use an adapter to manage if we may delete the object
        # that checks if the user has the 'Delete objects' permission
        # on the content by default but that could be overrided
        if IContentDeletable(obj).mayDelete():
            msg = {'message': _('object_deleted'),
                   'type': 'info'}
            # remove the object
            # just manage BeforeDeleteException because we rise it ourselves
            from OFS.ObjectManager import BeforeDeleteException
            try:
                unrestrictedRemoveGivenObject(obj)
            except BeforeDeleteException, exc:
                # abort because element was removed
                transaction.abort()
                msg = {'message': u'{0} ({1})'.format(
                    exc.message, exc.__class__.__name__),
                    'type': 'error'}
                if not catch_before_delete_exception:
                    raise BeforeDeleteException(exc.message)
        else:
            # as the action calling delete_givenuid is already protected by the check
            # made in the 'if' here above, if we arrive here it is that user is doing
            # something wrong, we raise Unauthorized
            raise Unauthorized

        # Redirect the user to the correct page and display the correct message.
        self.portal.plone_utils.addPortalMessage(**msg)
        if redirect and not msg['type'] == 'error':
            return self._findViewablePlace(obj)

    def _findViewablePlace(self, obj):
        '''
          Find a place the current user may access.
          By default, it will try to find a viewable parent.
        '''
        # redirect to HTTP_REFERER if it is not delete object
        if not self.request['HTTP_REFERER'].startswith(self.context.absolute_url()):
            return self.request['HTTP_REFERER']
        parent = obj.aq_inner.aq_parent
        member = api.user.get_current()
        while (not member.has_permission('View', parent) and not parent.meta_type == 'Plone Site'):
            parent = parent.aq_inner.aq_parent
        return parent.absolute_url()


class AsyncActionsPanelView(BrowserView):
    """ """

    def _convert_form_values(self):
        """As values are sent by JS, we need to change 'false' to False, 'true' to True, ..."""
        values = {key: json.loads(value) for key, value in self.request.form.items()}
        return values

    def __call__(self, **kwargs):
        """ """
        kwargs.update(self._convert_form_values())
        rendered_actions_panel = self.context.restrictedTraverse('@@actions_panel')(**kwargs)
        return rendered_actions_panel
