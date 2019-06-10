# vim: set fileencoding=utf-8 :
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from chibi_user.models import User


class User_admin_change_form( UserChangeForm ):
    class Meta( UserChangeForm.Meta ):
        model = User


class User_admin( UserAdmin ):
    form = User_admin_change_form


admin.site.register( User, User_admin )
