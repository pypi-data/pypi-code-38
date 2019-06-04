from register.forms.childcare import ChildCareForm
from register.models.childcare import ChildCare
from register.views.core import RegisterStep


class ChildCareView(RegisterStep):
    template_name = 'register/page/childcare.html'
    title = 'Child Care'
    form_class = ChildCareForm

    def get_initial(self):
        user = self.request.user
        initial = {}

        try:
            child_care = user.attendee.child_care
        except ChildCare.DoesNotExist:
            return initial

        initial['child_care'] = True

        for field in child_care._meta.get_fields():
            if field.is_relation:
                continue
            initial[field.name] = getattr(child_care, field.name)

        return initial

    def form_valid(self, form):
        attendee = self.request.user.attendee
        data = form.cleaned_data.copy()

        if not data.pop('child_care'):
            ChildCare.objects.filter(attendee=attendee).delete()
            return super().form_valid(form)

        child_care, created = ChildCare.objects.update_or_create(
            attendee=attendee, defaults=data)
        attendee.child_care = child_care

        return super().form_valid(form)
