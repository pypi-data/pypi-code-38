from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import REDIRECT_FIELD_NAME, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView

from acmin.forms import LoginForm
from acmin.models import User
from acmin.utils import attr
from .create import AdminCreateView
from .update import AdminUpdateView

app_name = __name__.split(".")[0]


class Mixin(object):
    model = User

    def form_valid(self, form):
        user = form.save(False)
        password = form.cleaned_data['password1']
        if password and len(password) > 0:
            user.set_password(password)
            user.save()
        return super().form_valid(form)

    def get_form_class(self):
        form_class = super().get_form_class()

        class UserForm(form_class):
            password1 = forms.CharField(label='修改密码', min_length=6, max_length=30, widget=forms.PasswordInput, required=False, help_text=u"如果需要更改密码,请直接填写. 否则就留空")
            password2 = forms.CharField(label='确认密码', min_length=6, max_length=30, widget=forms.PasswordInput, required=False)

            def clean_password2(self):
                password1 = self.cleaned_data.get('password1')
                password2 = self.cleaned_data.get('password2')
                if password1 and len(password1) > 0 and password1 != password2:
                    raise forms.ValidationError("两次密码输入不一致!")
                return password2

        return UserForm


class UserCreateView(Mixin, AdminCreateView):
    pass


class UserUpdateView(Mixin, AdminUpdateView):
    pass


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'acmin/admin/user/login.html'
    success_url = '/'
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, request, *args, **kwargs):
        self.request = request
        logout(request)
        return super().get(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if redirect_to is None:
            redirect_to = attr(settings, 'INDEX_URL')
        kwargs['redirect_to'] = redirect_to

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            # redirect_to = self.request.GET.get(self.redirect_field_name)
            auth.login(self.request, form.get_user())
            return super().form_valid(form)
            # return HttpResponseRedirect('/')
        else:
            return self.render_to_response({'form': form})

    def get_success_url(self):
        redirect_to = self.request.POST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            redirect_to = self.success_url
        return redirect_to
