from django.forms import Form

from directory_forms_api_client import actions


class AbstractActionMixin:

    @property
    def action_class(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        action = self.action_class(*args, **kwargs)
        return action.save(self.serialized_data)

    @property
    def serialized_data(self):
        return self.cleaned_data


class EmailActionMixin(AbstractActionMixin):
    action_class = actions.EmailAction

    @property
    def serialized_data(self):
        return {
            'text_body': self.text_body,
            'html_body': self.html_body,
        }

    @property
    def text_body(self):
        raise NotImplementedError()

    @property
    def html_body(self):
        raise NotImplementedError()


class ZendeskActionMixin(AbstractActionMixin):
    action_class = actions.ZendeskAction


class GovNotifyActionMixin(AbstractActionMixin):
    action_class = actions.GovNotifyAction


class PardotActionMixin(AbstractActionMixin):
    action_class = actions.PardotAction


class EmailAPIForm(EmailActionMixin, Form):
    pass


class ZendeskAPIForm(ZendeskActionMixin, Form):
    pass


class GovNotifyAPIForm(GovNotifyActionMixin, Form):
    pass


class PardotAPIForm(PardotActionMixin, Form):
    pass
