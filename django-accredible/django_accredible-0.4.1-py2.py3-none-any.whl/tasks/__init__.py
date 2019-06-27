from celery import current_app as app

from .create_accredible_group import CreateAccredibleGroupTask  # noqa
from .create_accredible_consultant_role_group import CreateAccredibleConsultantRoleGroupTask  # noqa
from .create_accredible_simple_credential import CreateAccredibleSimpleCredentialTask  # noqa
from .create_accredible_group_credential import CreateAccredibleGroupCredentialTask  # noqa
from .delete_accredible_group import DeleteAccredibleGroupTask  # noqa
from .update_accredible_group import UpdateAccredibleGroupTask  # noqa

app.tasks.register(CreateAccredibleGroupTask())
app.tasks.register(CreateAccredibleConsultantRoleGroupTask())
app.tasks.register(CreateAccredibleSimpleCredentialTask())
app.tasks.register(CreateAccredibleGroupCredentialTask())
app.tasks.register(DeleteAccredibleGroupTask())
app.tasks.register(UpdateAccredibleGroupTask())
