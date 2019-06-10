from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
""" import custom model here. """
from .models import UserModel
""" import custom form here. """
from .forms import UserForm
""" import auth forms here. """
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import UserChangeForm
# from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
""" import custom auth form here. """
from .forms import RegistrationForm
from .forms import EditProfileForm
from .forms import SigninForm
""" import auth func here. """
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


""" password protected view, account view. """
@login_required()
def AccountView(request):
    template_name = 'djangoadmin/djangoadmin/account_view_dashboard.html'
    context = { }
    return render(request, template_name, context)


""" password protected view, profile view. """
@login_required()
def ProfileView(request):
    template_name = 'djangoadmin/djangoadmin/profile_view_dashboard.html'
    context = { 'user': request.user }
    return render(request, template_name, context)


""" password protected view, Edit profile view. """
@login_required()
def EditProfileView(request):
    user = request.user
    template_name = 'djangoadmin/djangoadmin/edit_profile_view_form.html'
    if request.method == "POST":
        userchangeform = EditProfileForm(request.POST or None, instance=request.user)
        userform = UserForm(request.POST or None, request.FILES or None, instance=request.user.usermodel)
        if userchangeform.is_valid() and userform.is_valid():
            userchangeform.save()
            userform.save()
            messages.success(request, f"Hello!, {user.first_name}, Your profile edited successfully.", extra_tags='success')
            return redirect('djangoadmin:profile_view')
        else:
            messages.error(request, f"Hello!, {user.first_name}, Somthing went wrong, Try again.", extra_tags='error')
            return redirect('djangoadmin:edit_profile_view')
    else:
        userchangeform = EditProfileForm(instance=request.user)
        userform = UserForm(instance=request.user.usermodel)
        context = { 'userchangeform': userchangeform, 'userform': userform }
        return render(request, template_name, context)


""" password protected view, password change view. """
@login_required()
def PasswordChangeView(request):
    user = request.user
    template_name = 'djangoadmin/djangoadmin/password_change_view_form.html'
    if request.method == "POST":
        passwordchangeform = PasswordChangeForm(data=request.POST, user=request.user)
        if passwordchangeform.is_valid():
            passwordchangeform.save()
            messages.success(request, f"Hello!, {user.first_name}, Your password changed successfully.", extra_tags='success')
            return redirect('djangoadmin:profile_view')
        else:
            messages.error(request, f"Hello!, {user.first_name}, Somthing went wrong, Try again.", extra_tags='error')
            return redirect('djangoadmin:password_change_view')
    else:
        passwordchangeform = PasswordChangeForm(user=request.user)
        context = { 'passwordchangeform': passwordchangeform }
        return render(request, template_name, context)


""" signup view. """
def SignupView(request):
    template_name = 'djangoadmin/djangoadmin/signup_view_form.html'
    if request.method == 'POST':
        usercreationform = RegistrationForm(request.POST)
        if usercreationform.is_valid():
            user = usercreationform.save()
            login(request, user)
            messages.success(request, f"Hello!, {user.first_name} Welcome to Djangoengine.", extra_tags='success')
            return redirect('djangoadmin:account_view')
        else:
            messages.error(request, "Ohh!, Something went wrong, Please try again.", extra_tags='warning')
            return redirect('djangoadmin:signup_view')
    else:
        usercreationform = RegistrationForm()
        context = { 'usercreationform': usercreationform }
        return render(request, template_name, context)


""" login view. """
def LoginView(request):
    template_name = 'djangoadmin/djangoadmin/login_view_form.html'
    if request.method == 'POST':
        authenticationform = SigninForm(data=request.POST)
        if authenticationform.is_valid():
            user = authenticationform.get_user()
            login(request, user)
            if 'next' in request.POST:
                messages.success(request, f"{user.first_name} Loged in successfully.", extra_tags='success')
                return redirect(request.POST.get('next'))
            else:
                messages.success(request, f"{user.first_name} Loged in successfully.", extra_tags='success')
                return redirect('djangoadmin:account_view')
        else:
            messages.error(request, 'Something went wrong, please try again', extra_tags='warning')
            return redirect('djangoadmin:login_view')
    else:
        authenticationform = SigninForm()
        context = { 'authenticationform': authenticationform }
        return render(request, template_name, context)


""" logout view. """
@login_required()
def LogoutView(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logout successfully.', extra_tags='success')
        return redirect('djangoadmin:login_view')
