from ..signals_define import (
    create_certification_group,
    create_certification_credential,
    create_certification_group_credential,
    delete_certification_group,
    update_certification_group)

from .create_certification import (
    create_accredible_handler,
    create_credential_accredible_handler,
    create_group_and_credentials_handler,
    delete_accredible_handler,
    update_certification_group_handler)


def setup_signals():
    create_certification_group.connect(create_accredible_handler)
    delete_certification_group.connect(delete_accredible_handler)
    create_certification_credential.connect(create_credential_accredible_handler)
    create_certification_group_credential.connect(
        create_group_and_credentials_handler)
    update_certification_group.connect(
        update_certification_group_handler)
