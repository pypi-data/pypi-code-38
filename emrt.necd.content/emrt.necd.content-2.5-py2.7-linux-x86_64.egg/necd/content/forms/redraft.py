from datetime import datetime
from z3c.form import button
from z3c.form import form, field
from plone.z3cform.layout import wrap_form
import plone.api as api
from emrt.necd.content.commentextender import ICommentExtenderFields
from emrt.necd.content.constants import ROLE_LR


class RedraftQuestionForm(form.Form):
    fields = field.Fields(ICommentExtenderFields).select('redraft_message')
    ignoreContext = True

    def update(self):
        super(RedraftQuestionForm, self).update()
        question = self.context.aq_parent
        roles = api.user.get_roles(obj=self.context)
        is_lr = ROLE_LR in roles or 'Manager' in roles
        if not is_lr:
            self.request.response.redirect(question.absolute_url())

    def updateWidgets(self):
        super(RedraftQuestionForm, self).updateWidgets()
        self.widgets['redraft_message'].rows = 15

    def updateActions(self):
        super(RedraftQuestionForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')

    @button.buttonAndHandler(u'Ask SE to redraft')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        message = data['redraft_message']
        if message:
            self.context.redraft_message = message
            self.context.redraft_date = datetime.now()

        question = self.context.aq_parent
        api.content.transition(
            obj=question,
            transition='redraft',
            comment=self.context.getId(),
        )
        self.request.response.redirect(question.absolute_url())

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        question = self.context.aq_parent
        self.request.response.redirect(question.absolute_url())


RedraftQuestionView = wrap_form(RedraftQuestionForm)
