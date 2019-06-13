from urllib.parse import urlparse

from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, render_to_response

# Create your views here.


# helper method to generate a context csrf_token
# and adding a login form in this context
from django.template.context_processors import csrf
from django.utils.http import urlunquote, is_safe_url
from django.views import View


# Create your views here.
from .models import CustomUserCreationForm


def index(request):
    return render(request, "accounts_index.html")


def create_context_username_csrf(request):
    context = {}
    context.update(csrf(request))
    context["login_form"] = AuthenticationForm
    return context


def get_next_url(request):
    next = request.META.get("HTTP_REFERER")
    if next:
        next = urlunquote(next)  # HTTP_REFERER may be encoded.
    if not is_safe_url(url=next, allowed_hosts=request.get_host()):
        next = "/"
    return next


class LoginView(View):
    def get(self, request):
        # if the user is logged in, then do a redirect to the home page
        if auth.get_user(request).is_authenticated:
            return redirect("/")
        else:
            # Otherwise, form a context with the authorization form
            # and we return to this page context.
            # It works, for url - /admin/login/ and for /accounts/login/
            context = create_context_username_csrf(request)
            return render_to_response("login.html", context=context)

    def post(self, request):
        # having received the authorization request
        form = AuthenticationForm(request, data=request.POST)

        # check the correct form, that there is a user and he entered the correct password
        print(form.is_valid())
        if form.is_valid():
            # if successful authorizing user
            auth.login(request, form.get_user())
            # get previous url
            next = urlparse(get_next_url(request)).path
            # and if the user of the number of staff and went through url /admin/login/
            # then redirect the user to the admin panel
            if next == "/admin/login/" and request.user.is_staff:
                return redirect("/admin/")
            # otherwise do a redirect to the previous page,
            # in the case of a / accounts / login / will happen is another redirect to the home page
            # in the case of any other url, will return the user to the url
            return redirect(next)

        # If not true, then the user will appear on the login page
        # and see an error message
        context = create_context_username_csrf(request)
        context["login_form"] = form

        return render_to_response("login.html", context=context)


def pagelogout(request):
    logout(request)
    return redirect("index")


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("index")
        return render(request, "register.html", {"form": form})
