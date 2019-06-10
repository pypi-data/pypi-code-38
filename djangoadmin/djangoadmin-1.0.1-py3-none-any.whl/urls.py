# Removing this Comment Section violate The License Terms and 'Terms and Condition'.
"""
#################################################################################
Removing this Comment Section violate The License Terms and 'Terms and Condition'.
This Software 'Djangoadmin' published under the MIT  License. Permission is hereby
granted, free of  charge,  to any person obtaining  a copy  of this  software and
associated documentation  files (the "Software"), to deal  in the Software without
restriction, including  without  limitation the rights to use, copy, modify,merge,
publish,  distribute,  sublicense,  and/or   sell  copies of the Software, and  to
permit persons to whom the  Software  is  furnished  to  do  so,  subject  to  the
following conditions:

The above  copyright notice and  this permission  notice shall be included  in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF    MERCHANTABILITY,  FITNESS  FOR  A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR   COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ###############################################################################
You can contact to Author here.
Author : Vinit bhjram pawar
Email : bhojrampawar@hotmail.com
Website : vinitpawar.com
# ###############################################################################
"""


from django.conf.urls import re_path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


# Define the app name here.
app_name = "djangoadmin"


# urlspattern goes here.
urlpatterns = [
    re_path(r'^account/$', views.AccountView, name='account_view'),
    re_path(r'^profile/$', views.ProfileView, name='profile_view'),
    re_path(r'^profile/edit/$', views.EditProfileView, name="edit_profile_view"),
    re_path(r'^register/$', views.SignupView, name="signup_view"),
    re_path(r'^login/$', views.LoginView, name="login_view"),
    re_path(r'^password-change/$', views.PasswordChangeView, name="password_change_view"),
    re_path(r'^password-reset/$', auth_views.PasswordResetView.as_view(template_name="djangoadmin/djangoadmin/password_reset_view.html", email_template_name='djangoadmin/djangoadmin/password_reset_email.html', success_url=reverse_lazy('djangoadmin:password_reset_done')), name="password_reset"),
    re_path(r'^password-reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name="djangoadmin/djangoadmin/password_reset_done_view.html"), name="password_reset_done"),
    re_path(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(template_name="djangoadmin/djangoadmin/password_reset_confirm_view.html", success_url=reverse_lazy('djangoadmin:password_reset_complete')), name="password_reset_confirm"),
    re_path(r'^password-reset-complete/$', auth_views.PasswordResetCompleteView.as_view(template_name="djangoadmin/djangoadmin/password_reset_complete_view.html"), name="password_reset_complete"),
    re_path(r'^logout/$', views.LogoutView, name="logout_view"),
]
