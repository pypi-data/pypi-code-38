from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView


class ConfirmTransitionView(BrowserView):
    '''
      This manage the overlay popup displayed when a transition needs to be confirmed.
      For other transitions, this views is also used but the confirmation popup is not shown.
    '''
    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.actionspanel_view_name = self.request.get('actionspanel_view_name', 'actions_panel')

    def __call__(self):
        form = self.request.form
        # either we received form.submitted in the request because we are triggering
        # a transition that does not need a confirmation or we clicked on the save button of
        # the confirmation popup
        submitted = form.get('form.buttons.save', False) or form.get('form.submitted') == '1'
        cancelled = form.get('form.buttons.cancel', False)
        actionspanel_view = self.context.restrictedTraverse('@@%s' % self.actionspanel_view_name)
        if cancelled:
            # the only way to enter here is the popup overlay not to be shown
            # because while using the popup overlay, the jQ function take care of hidding it
            # while the Cancel button is hit
            return self.request.response.redirect(self.context.absolute_url())
        elif submitted:
            return actionspanel_view.triggerTransition(transition=self.request.get('transition'),
                                                       comment=self.request.get('comment'),
                                                       redirect=bool(self.request.get('redirect') == '1'))
        return self.index()

    @memoize
    def initTransition(self):
        '''Initialize values for the 'transition' form field.'''
        res = {}
        actionspanel_view = self.context.restrictedTraverse('@@%s' % self.actionspanel_view_name)
        availableTransitions = actionspanel_view.getTransitions()
        for availableTransition in availableTransitions:
            if self.request.get('transition') == availableTransition['id'] and \
               availableTransition['confirm'] is True:
                res['id'] = self.request.get('transition')
                res['confirm'] = False
        return res

    def transition_title(self):
        '''Returns transition title.'''
        actionspanel_view = self.context.restrictedTraverse('@@%s' % self.actionspanel_view_name)
        availableTransitions = actionspanel_view.getTransitions()
        for availableTransition in availableTransitions:
            if self.request.get('transition') == availableTransition['id']:
                return availableTransition['title']
