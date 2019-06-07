from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class CMISObjectType(DjangoChoices):
    zaken = ChoiceItem("F:drc:zaken", _("Zaken hoofd folder"))
    zaak_folder = ChoiceItem("F:drc:zaak", _("Zaak folder"))
    edc = ChoiceItem("D:drc:document", _("Enkelvoudig document"))


class CMISCapabilities(DjangoChoices):
    """
    http://docs.oasis-open.org/cmis/CMIS/v1.0/cmis-spec-v1.0.html
    """

    changes = ChoiceItem(
        "Changes", _('Indicates what level of changes (if any) the repository exposes via the "change log" service.')
    )
    all_versions_searchable = ChoiceItem(
        "AllVersionsSearchable",
        _(
            "Ability of the Repository to include all versions of document. If False, typically either the latest or the latest major version will be searchable."
        ),
    )
    content_stream_updatability = ChoiceItem(
        "ContentStreamUpdatability",
        _("Indicates the support a repository has for updating a document's content stream."),
    )
    pwc_updatable = ChoiceItem(
        "PWCUpdatable", _('Ability for an application to update the "Private Working Copy" of a checked-out document.')
    )
    pwc_searchable = ChoiceItem(
        "PWCSearchable",
        _(
            'Ability of the Repository to include the "Private Working Copy" of checked-out documents in query search scope; otherwise PWC\'s are not searchable'
        ),
    )
    unfiling = ChoiceItem(
        "Unfiling",
        _("Ability for an application to leave a document or other file-able object not filed in any folder."),
    )
    multifiling = ChoiceItem(
        "Multifiling",
        _("Ability for an application to file a document or other file-able object in more than one folder."),
    )
    version_specific_filing = ChoiceItem(
        "VersionSpecificFiling",
        _("Ability for an application to file individual versions (i.e., not all versions) of a document in a folder."),
    )
    renditions = ChoiceItem(
        "Renditions", _("Indicates whether or not the repository exposes renditions of document or folder objects.")
    )
    query = ChoiceItem("Query", _("Indicates the types of queries that the Repository has the ability to fulfill."))
    get_folder_tree = ChoiceItem(
        "GetFolderTree", _("Ability for an application to retrieve the folder tree via the getFolderTree service.")
    )
    acl = ChoiceItem("ACL", _("Indicates the level of support for ACLs by the repository."))
    join = ChoiceItem("Join", _(" Indicates the types of JOIN keywords that the Repository can fulfill in queries."))
