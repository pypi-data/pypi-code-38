"""
    Common views
"""
import copy
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import IntegrityError
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from password_policies.views import PasswordChangeFormView

from core_dashboard_common_app import constants as dashboard_constants
from core_dashboard_common_app import settings
from core_dashboard_common_app.views.common.forms import ActionForm, UserForm
from core_main_app.components.blob import api as blob_api, utils as blob_utils
from core_main_app.components.data import api as data_api
from core_main_app.components.template import api as template_api
from core_main_app.components.template_version_manager import api as template_version_manager_api
from core_main_app.components.user import api as user_api
from core_main_app.components.user.api import get_id_username_dict
from core_main_app.components.workspace import api as workspace_api
from core_main_app.settings import INSTALLED_APPS
from core_main_app.utils.access_control.exceptions import AccessControlError
from core_main_app.utils.datetime_tools.date_time_encoder import DateTimeEncoder
from core_main_app.utils.pagination.django_paginator.results_paginator import ResultsPaginator
from core_main_app.utils.rendering import render
from core_main_app.views.admin.forms import EditProfileForm
from core_main_app.views.common.ajax import EditTemplateVersionManagerView
from core_main_app.views.common.views import CommonView
from core_main_app.views.user.forms import WorkspaceForm
import core_main_app.components.data.api as workspace_data_api
from core_main_app.utils.labels import get_data_label

if 'core_curate_app' in INSTALLED_APPS:
    import core_curate_app.components.curate_data_structure.api as curate_data_structure_api
if 'core_composer_app' in INSTALLED_APPS:
    from core_composer_app.components.type_version_manager import api as type_version_manager_api
    from core_composer_app.components.type import api as type_api


@login_required(login_url=reverse_lazy("core_main_app_login"))
def home(request):
    """ Home page.

    Args:
        request:

    Returns:
    """
    return render(request, dashboard_constants.DASHBOARD_HOME_TEMPLATE)


@login_required(login_url=reverse_lazy("core_main_app_login"))
def my_profile(request):
    """ User's profile information page.

    Args:
        request:

    Returns:
    """
    return render(request, dashboard_constants.DASHBOARD_PROFILE_TEMPLATE)


@login_required(login_url=reverse_lazy("core_main_app_login"))
def my_profile_edit(request):
    """ Edit the profile.

    Args:
        request:

    Returns:
    """
    if request.method == 'POST':
        form = _get_edit_profile_form(request=request, url=dashboard_constants.DASHBOARD_PROFILE_EDIT_TEMPLATE)
        if form.is_valid():
            user = request.user
            user.first_name = request.POST['firstname']
            user.last_name = request.POST['lastname']
            user.email = request.POST['email']
            try:
                user_api.upsert(user)
            except IntegrityError as e:
                if 'unique constraint' in e.message:
                    message = "A user with the same username already exists."
                    return render(request, dashboard_constants.DASHBOARD_PROFILE_EDIT_TEMPLATE,
                                  context={'form': form, 'action_result': message})
                else:
                    _error_while_saving(request, form)
            except Exception, e:
                _error_while_saving(request, form)

            messages.add_message(request, messages.INFO, 'Profile information edited with success.')
            return HttpResponseRedirect(reverse("core_dashboard_profile"))
    else:
        user = request.user
        data = {'firstname': user.first_name,
                'lastname': user.last_name,
                'username': user.username,
                'email': user.email}
        form = _get_edit_profile_form(request, dashboard_constants.DASHBOARD_PROFILE_TEMPLATE, data)

    return render(request, dashboard_constants.DASHBOARD_PROFILE_EDIT_TEMPLATE, context={'form': form})


def _get_edit_profile_form(request, url, data=None):
    """ Edit the profile.

    Args:
        request
        url
        data

    Returns:
    """
    data = request.POST if data is None else data
    try:
        return EditProfileForm(data)
    except Exception as e:
        message = "A problem with the form has occurred."
        return render(request, url,
                      context={'action_result': message})


def _error_while_saving(request, form):
    """ Raise exception if uncatched problems occurred while saving.

    Args:
        request
        form

    Returns:
    """
    message = "A problem has occurred while saving the user."
    return render(request, dashboard_constants.DASHBOARD_PROFILE_EDIT_TEMPLATE,
                  context={'form': form, 'action_result': message})


class UserDashboardPasswordChangeFormView(PasswordChangeFormView):

    def get(self, request, *args, **kwargs):
        """

        Args: request:
        Args: args:
        Args: kwargs:
        Returns:
        """
        return render(request, self.template_name, context={'form': self.get_form()})

    def get_form(self):
        """ Return the form.

        Returns: The form.
        """

        return super(UserDashboardPasswordChangeFormView, self).get_form(self.form_class)

    def form_valid(self, form):
        """

        Args: form
        Returns:
        """
        messages.success(self.request, "Password changed with success.")
        return super(UserDashboardPasswordChangeFormView, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.

        Args: form
        Returns:
        """
        return render(self.request, self.template_name, context={'form': form})

    def get_success_url(self):
        """
        Returns a query string field with a previous URL if available (Mimicing
        the login view. Used on forced password changes, to know which URL the
        user was requesting before the password change.)
        If not returns the :attr:`~PasswordChangeFormView.success_url` attribute
        if set, otherwise the URL to the :class:`PasswordChangeDoneView`.
        """
        checked = '_password_policies_last_checked'
        last = '_password_policies_last_changed'
        required = '_password_policies_change_required'
        now = json.dumps(timezone.now(), cls=DateTimeEncoder)
        self.request.session[checked] = now
        self.request.session[last] = now
        self.request.session[required] = False
        redirect_to = self.request.POST.get(self.redirect_field_name, '')
        if redirect_to:
            url = redirect_to
        elif self.success_url:
            url = self.success_url
        else:
            url = reverse('password_change_done')
        return url


class DashboardRecords(CommonView):
    """ List the records.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE
    data_template = dashboard_constants.DASHBOARD_RECORDS_TEMPLATE_TABLE_PAGINATION
    document = dashboard_constants.FUNCTIONAL_OBJECT_ENUM.RECORD
    allow_change_workspace_if_public = True

    def can_change_workspace(self, data):
        """ Check if you can change the workspace.

        Args:

        Returns:
        """

        workspace = data.workspace
        if workspace is not None and workspace_api.is_workspace_public(workspace) and not self.allow_change_workspace_if_public:
            return False
        return True

    def get(self, request, *args, **kwargs):

        # Get records
        if self.administration:
            try:
                loaded_data = data_api.get_all(request.user, '-last_modification_date')
            except AccessControlError, ace:
                loaded_data = []
        else:
            loaded_data = data_api.get_all_by_user(request.user, '-last_modification_date')

        # Paginator
        page = request.GET.get('page', 1)
        results_paginator = ResultsPaginator.get_results(loaded_data, page, settings.RECORD_PER_PAGE_PAGINATION)

        # Data context
        results_paginator.object_list = self._format_data_context(results_paginator.object_list)

        # Add user_form for change owner
        user_form = UserForm(request.user)
        context = {
            'number_total': loaded_data.count,
            'user_data': results_paginator,
            'user_form': user_form,
            'document': self.document,
            'template': self.data_template,
            'action_form': ActionForm([('1', 'Delete selected records'),
                                       ('2', 'Change owner of selected records')]),
            'menu': self.administration,
            'administration': self.administration
        }
        if self.administration:
            context.update({'username_list': get_id_username_dict(user_api.get_all_users())})

        modals = ["core_main_app/user/workspaces/list/modals/assign_workspace.html",
                  dashboard_constants.MODALS_COMMON_DELETE,
                  dashboard_constants.MODALS_COMMON_CHANGE_OWNER
                  ]

        assets = self._get_assets()

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)

    def _format_data_context(self, data_list):
        data_context_list = []
        for data in data_list:
            data_context_list.append({'data': data,
                                      'can_read': True,
                                      'can_write': True,
                                      'is_owner': True,
                                      'can_change_workspace': self.can_change_workspace(data)})
        return data_context_list

    def _get_assets(self):
        assets = {
            "css": copy.deepcopy(dashboard_constants.CSS_COMMON),

            "js": [
                {
                    "path": 'core_main_app/user/js/workspaces/list/modals/assign_workspace.js',
                    "is_raw": False
                },
                {
                    "path": 'core_dashboard_common_app/common/js/init_pagination.js',
                    "is_raw": False
                },
                {
                    "path": 'core_dashboard_common_app/user/js/init.raw.js',
                    "is_raw": True
                },
                {
                    "path": dashboard_constants.JS_EDIT_RECORD,
                    "is_raw": False
                },
                {
                    "path": dashboard_constants.JS_VIEW_RECORD,
                    "is_raw": False
                },
                {
                    "path": dashboard_constants.JS_COMMON_FUNCTION_CHANGE_OWNER,
                    "is_raw": False
                },
                {
                    "path": dashboard_constants.JS_COMMON_FUNCTION_DELETE,
                    "is_raw": False
                }
            ]
        }

        # Admin
        if self.administration:
            assets['js'].append({
                "path": dashboard_constants.ADMIN_VIEW_RECORD_RAW,
                "is_raw": True
            })
            assets['js'].append({
                "path": 'core_dashboard_common_app/admin/js/action_dashboard.js',
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_COUNT_CHECK,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_RESET_CHECKBOX,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_SELECT_ALL,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_SELETED_ELEMENT,
                "is_raw": False
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_INIT_MENU,
                "is_raw": False
            })
        else:
            assets['js'].append({
                "path": dashboard_constants.JS_USER_SELECTED_ELEMENT,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.USER_VIEW_RECORD_RAW,
                "is_raw": True
            })

        return assets


class DashboardFiles(CommonView):
    """ List the files.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE

    def get(self, request, *args, **kwargs):
        """ Method GET

        Args:
            request:
            args:
            kwargs:

        Returns:
        """
        if self.administration:
            files = blob_api.get_all()
        else:
            files = blob_api.get_all_by_user_id(request.user.id)

        detailed_file = []
        for file in files:
            detailed_file.append({'user': user_api.get_user_by_id(file.user_id).username,
                                  'date': file.id.generation_time,
                                  'file': file,
                                  'url': blob_utils.get_blob_download_uri(file, request)
                                  })

        context = {
            'administration': self.administration,
            'number_total': files.count,
            'user_data': detailed_file,
            'document': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.FILE,
            'template': dashboard_constants.DASHBOARD_FILES_TEMPLATE_TABLE,
            'menu': self.administration,
        }

        if self.administration:
            context.update({'action_form': ActionForm([('1', 'Delete selected files')])
                            })

        modals = [dashboard_constants.MODALS_COMMON_DELETE]

        assets = {
            "css": dashboard_constants.CSS_COMMON,

            "js": [
                    {
                        "path": 'core_dashboard_common_app/user/js/init.raw.js',
                        "is_raw": True
                    },
                    {
                        "path": dashboard_constants.JS_COMMON_FUNCTION_DELETE,
                        "is_raw": False
                    },
                    {
                        "path": dashboard_constants.JS_USER_SELECTED_ELEMENT,
                        "is_raw": True
                    }
            ]
        }

        if "core_file_preview_app" in INSTALLED_APPS:
            assets["js"].extend([
                {
                    "path": 'core_file_preview_app/user/js/file_preview.js',
                    "is_raw": False
                }
            ])
            assets["css"].append("core_file_preview_app/user/css/file_preview.css")
            modals.append("core_file_preview_app/user/file_preview_modal.html")

        # Admin
        if self.administration:
            assets['js'].append({
                "path": 'core_dashboard_common_app/common/js/init_pagination.js',
                "is_raw": False
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_ACTION_DASHBOARD,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_COUNT_CHECK,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_RESET_CHECKBOX,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_SELECT_ALL,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_SELETED_ELEMENT,
                "is_raw": False
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_INIT_MENU,
                "is_raw": False
            })

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)


class DashboardForms(CommonView):
    """ List the forms.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE
    document = dashboard_constants.FUNCTIONAL_OBJECT_ENUM.FORM

    def get(self, request, *args, **kwargs):
        """ Method GET

        Args:
            request:
            args:
            kwargs:

        Returns:
        """

        # Get the forms
        if self.administration:
            forms = curate_data_structure_api.get_all_with_no_data()
        else:
            forms = curate_data_structure_api.get_all_by_user_id_with_no_data(request.user.id)
        detailed_forms = self._get_detailed_forms(forms)

        context = {'administration': self.administration,
                   'number_total': forms.count,
                   'user_data': detailed_forms,
                   'user_form': UserForm(request.user),
                   'document': self.document,
                   'template': dashboard_constants.DASHBOARD_FORMS_TEMPLATE_TABLE,
                   'menu': self.administration
                   }

        modals = [dashboard_constants.MODALS_COMMON_DELETE,
                  dashboard_constants.MODALS_COMMON_CHANGE_OWNER
                  ]

        assets = {
            "css": dashboard_constants.CSS_COMMON,

            "js": [{
                        "path": dashboard_constants.JS_COMMON_FUNCTION_DELETE,
                        "is_raw": False
                    },
                    {
                        "path": dashboard_constants.JS_COMMON_FUNCTION_CHANGE_OWNER,
                        "is_raw": False
                    },
                    {
                        "path": 'core_dashboard_common_app/user/js/init.raw.js',
                        "is_raw": True
                    },
            ]
        }

        if self.administration:
            # Get all username and corresponding ids
            user_names = dict((str(x.id), x.username) for x in user_api.get_all_users())
            context.update({'usernames': user_names,
                            'action_form': ActionForm(
                                [('1', 'Delete selected forms'), ('2', 'Change owner of selected forms')]),
                            })

            assets['js'].extend([{
                                    "path": 'core_dashboard_common_app/common/js/init_pagination.js',
                                    "is_raw": False
                                },
                                {
                                    "path": dashboard_constants.JS_ADMIN_ACTION_DASHBOARD,
                                    "is_raw": True
                                },
                                {
                                    "path": dashboard_constants.JS_ADMIN_COUNT_CHECK,
                                    "is_raw": True
                                },
                                {
                                    "path": dashboard_constants.JS_ADMIN_RESET_CHECKBOX,
                                    "is_raw": True
                                },
                                {
                                    "path": dashboard_constants.JS_ADMIN_SELECT_ALL,
                                    "is_raw": True
                                },
                                {
                                    "path": dashboard_constants.JS_ADMIN_SELETED_ELEMENT,
                                    "is_raw": False
                                },
                                {
                                    "path": dashboard_constants.JS_ADMIN_INIT_MENU,
                                    "is_raw": False
                                }])
        else:
            assets['js'].append({
                "path": dashboard_constants.JS_USER_SELECTED_ELEMENT,
                "is_raw": True
            })

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)

    def _get_detailed_forms(self, forms):

        detailed_forms = []
        for form in forms:
            detailed_forms.append({'form': form})
        return list(reversed(detailed_forms))


class DashboardTemplates(CommonView):
    """ List the templates.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE

    def get(self, request, *args, **kwargs):
        """ Method GET

        Args:
            request:
            args:
            kwargs:

        Returns:
        """
        # Get templates
        if self.administration:
            template_versions = template_version_manager_api.get_all()
        else:
            template_versions = template_version_manager_api.get_all_by_user_id(request.user.id)

        detailed_templates = []
        for template_version in template_versions:
            # If the version manager doesn't have a user, the template is global.
            if template_version.user is not None:
                detailed_templates.append({'template_version': template_version,
                                           'template': template_api.get(template_version.current),
                                           'user': user_api.get_user_by_id(template_version.user).username,
                                           'title': template_version.title
                                           })

        context = {
            'number_total': len(detailed_templates),
            'user_data': detailed_templates,
            'user_form': UserForm(request.user),
            'document': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.TEMPLATE,
            'object_name': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.TEMPLATE,
            'template': dashboard_constants.DASHBOARD_TEMPLATES_TEMPLATE_TABLE,
            'menu': False
        }

        modals = [
                    "core_main_app/admin/templates/list/modals/disable.html",
                    EditTemplateVersionManagerView.get_modal_html_path()
                ]

        assets = {
            "css": dashboard_constants.CSS_COMMON,

            "js": [
                {
                    "path": 'core_main_app/common/js/templates/list/restore.js',
                    "is_raw": False
                },
                {
                    "path": 'core_main_app/common/js/templates/list/modals/disable.js',
                    "is_raw": False
                },
                EditTemplateVersionManagerView.get_modal_js_path()]
        }

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)


class DashboardTypes(CommonView):
    """ List the types.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE

    def get(self, request, *args, **kwargs):
        """ Method GET

        Args:
            request:
            args:
            kwargs:

        Returns:
        """

        # Get types
        if self.administration:
            type_versions = type_version_manager_api.get_all_version_manager()
        else:
            type_versions = type_version_manager_api.get_version_managers_by_user(request.user.id)

        detailed_types = []
        for type_version in type_versions:
            # If the version manager doesn't have a user, the type is global.
            if type_version.user is not None:
                detailed_types.append({'type_version': type_version,
                                       'type': type_api.get(type_version.current),
                                       'user': user_api.get_user_by_id(type_version.user).username,
                                       'title': type_version.title})

        context = {
            'number_total': len(detailed_types),
            'user_form': UserForm(request.user),
            'document': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.TYPE,
            'object_name': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.TYPE,
            'template': dashboard_constants.DASHBOARD_TYPES_TEMPLATE_TABLE,
            'menu': False,
            'user_data': detailed_types
        }

        modals = [
            "core_main_app/admin/templates/list/modals/disable.html",
            EditTemplateVersionManagerView.get_modal_html_path()
        ]

        assets = {
            "css": dashboard_constants.CSS_COMMON,

            "js": [
                {
                    "path": 'core_main_app/common/js/templates/list/restore.js',
                    "is_raw": False
                },
                {
                    "path": 'core_main_app/common/js/templates/list/modals/disable.js',
                    "is_raw": False
                },
                EditTemplateVersionManagerView.get_modal_js_path()]
        }

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)


class DashboardWorkspaces(CommonView):
    """ List the workspaces.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE

    def get(self, request, *args, **kwargs):
        """ Method GET

        Args:
            request:
            args:
            kwargs:

        Returns:
        """

        if self.administration:
            user_workspaces = workspace_api.get_all()
        else:
            # Get the workspace the user can read
            user_workspace_read = list(workspace_api.get_all_workspaces_with_read_access_by_user(request.user))
            # Get the workspace the user can write
            user_workspace_write = list(workspace_api.get_all_workspaces_with_write_access_by_user(request.user))
            # Get the merged list without doublons
            user_workspaces = user_workspace_read + list(set(user_workspace_write) - set(user_workspace_read))

        detailed_user_workspaces = []
        for user_workspace in user_workspaces:
            detailed_user_workspaces.append({'user': user_api.get_user_by_id(user_workspace.owner).username if not workspace_api.is_workspace_global(user_workspace) else "GLOBAL",
                                             'is_owner': self.administration or user_workspace.owner == str(request.user.id),
                                             'name': user_workspace.title,
                                             'workspace': user_workspace,
                                             'can_read': self.administration or user_workspace in user_workspace_read,
                                             'can_write': self.administration or user_workspace in user_workspace_write,
                                             'is_public': workspace_api.is_workspace_public(user_workspace),
                                             'is_global': workspace_api.is_workspace_global(user_workspace)
                                             })

        context = {
            'number_total': len(user_workspaces),
            'workspace_form': WorkspaceForm(),
            'user_data': detailed_user_workspaces,
            'document': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.WORKSPACE,
            'template': dashboard_constants.DASHBOARD_WORKSPACES_TEMPLATE_TABLE,
            'create_workspace': not self.administration,
            'can_set_public': settings.CAN_SET_WORKSPACE_PUBLIC
        }

        modals = [dashboard_constants.MODALS_COMMON_DELETE]

        assets = {
            "css": copy.deepcopy(dashboard_constants.CSS_COMMON),

            "js": [
                {
                    "path": dashboard_constants.JS_USER_SELECTED_ELEMENT,
                    "is_raw": True
                },
                {
                    "path": dashboard_constants.JS_COMMON_FUNCTION_DELETE,
                    "is_raw": False
                },
                {
                    "path": 'core_dashboard_common_app/user/js/init.raw.js',
                    "is_raw": True
                },
            ]
        }

        if not self.administration:
            modals.append("core_main_app/user/workspaces/list/create_workspace.html")
            assets['js'].append({
                                    "path": 'core_main_app/user/js/workspaces/create_workspace.js',
                                    "is_raw": False
                                })

        if settings.CAN_SET_WORKSPACE_PUBLIC:
            modals.append("core_main_app/user/workspaces/list/modals/set_public.html")
            assets['js'].append({
                                    "path": 'core_main_app/user/js/workspaces/list/modals/set_public.js',
                                    "is_raw": False
                                })
            modals.append("core_main_app/user/workspaces/list/modals/set_private.html")
            assets['js'].append({
                                    "path": 'core_main_app/user/js/workspaces/list/modals/set_private.js',
                                    "is_raw": False
                                })

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)


class DashboardWorkspaceRecords(CommonView):
    """ List the records of a workspace.
    """

    template = dashboard_constants.DASHBOARD_TEMPLATE
    data_template = dashboard_constants.DASHBOARD_RECORDS_TEMPLATE_TABLE_PAGINATION

    def get(self, request, workspace_id, *args, **kwargs):
        workspace = workspace_api.get_by_id(workspace_id)

        try:
            workspace_data = workspace_data_api.get_all_by_workspace(workspace, request.user)
        except AccessControlError, ace:
            workspace_data = []

        user_can_read = workspace_api.can_user_read_workspace(workspace, request.user)
        user_can_write = workspace_api.can_user_write_workspace(workspace, request.user)

        # Paginator
        page = request.GET.get('page', 1)
        results_paginator = ResultsPaginator.get_results(workspace_data, page, settings.RECORD_PER_PAGE_PAGINATION)

        # Data context
        results_paginator.object_list = self._format_data_context(results_paginator.object_list, request.user,
                                                                  user_can_read, user_can_write)

        # Add user_form for change owner
        user_form = UserForm(request.user)
        context = {
            'number_total': workspace_data.count,
            'user_data': results_paginator,
            'user_form': user_form,
            'document': dashboard_constants.FUNCTIONAL_OBJECT_ENUM.RECORD,
            'template': self.data_template,
            'administration': self.administration,
            'username_list': get_id_username_dict(user_api.get_all_users())
        }

        # Get all username and corresponding ids
        user_names = dict((str(x.id), x.username) for x in user_api.get_all_users())
        context.update({'usernames': user_names})
        context.update({'title': 'List of ' + get_data_label() + 's of workspace: ' + workspace.title})

        modals = ["core_main_app/user/workspaces/list/modals/assign_workspace.html",
                  dashboard_constants.MODALS_COMMON_CHANGE_OWNER,
                  dashboard_constants.MODALS_COMMON_DELETE]

        assets = self._get_assets()

        return self.common_render(request, self.template,
                                  context=context,
                                  assets=assets,
                                  modals=modals)

    def _format_data_context(self, data_list, user, user_can_read, user_can_write):
        detailed_user_data = []
        for data in data_list:
            is_owner = str(data.user_id) == str(user.id) or self.administration
            detailed_user_data.append({'data': data,
                                       'can_read': user_can_read or is_owner,
                                       'can_write': user_can_write or is_owner,
                                       'is_owner': is_owner})
        return detailed_user_data

    def _get_assets(self):
        assets = {
            "css": copy.deepcopy(dashboard_constants.CSS_COMMON),

            "js": [{
                "path": 'core_main_app/user/js/workspaces/list/modals/assign_workspace.js',
                "is_raw": False
            },
                {
                    "path": 'core_main_app/common/js/backtoprevious.js',
                    "is_raw": True
                },
                {
                    "path": dashboard_constants.USER_VIEW_RECORD_RAW,
                    "is_raw": True
                },
                {
                    "path": dashboard_constants.JS_EDIT_RECORD,
                    "is_raw": False
                },
                {
                    "path": dashboard_constants.JS_VIEW_RECORD,
                    "is_raw": False
                },
                {
                    "path": 'core_dashboard_common_app/user/js/init.raw.js',
                    "is_raw": True
                },
                {
                    "path": 'core_dashboard_common_app/common/js/init_pagination.js',
                    "is_raw": False
                },
                {
                    "path": dashboard_constants.JS_COMMON_FUNCTION_CHANGE_OWNER,
                    "is_raw": False
                },
                {
                    "path": dashboard_constants.JS_COMMON_FUNCTION_DELETE,
                    "is_raw": False
                }
            ]
        }

        # Admin
        if self.administration:
            assets['js'].append({
                "path": dashboard_constants.ADMIN_VIEW_RECORD_RAW,
                "is_raw": True
            })
            assets['js'].append({
                "path": 'core_dashboard_common_app/admin/js/action_dashboard.js',
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_COUNT_CHECK,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_RESET_CHECKBOX,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_SELECT_ALL,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_SELETED_ELEMENT,
                "is_raw": False
            })
            assets['js'].append({
                "path": dashboard_constants.JS_ADMIN_INIT_MENU,
                "is_raw": False
            })
        else:
            assets['js'].append({
                "path": dashboard_constants.JS_USER_SELECTED_ELEMENT,
                "is_raw": True
            })
            assets['js'].append({
                "path": dashboard_constants.USER_VIEW_RECORD_RAW,
                "is_raw": True
            })

        return assets
