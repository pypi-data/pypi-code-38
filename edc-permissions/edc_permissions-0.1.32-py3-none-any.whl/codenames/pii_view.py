from django.conf import settings

view_subjectconsent = ".view_".join(settings.SUBJECT_CONSENT_MODEL.split("."))
view_historicalsubjectconsent = ".view_historical".join(
    settings.SUBJECT_CONSENT_MODEL.split(".")
)


pii_view = [
    view_historicalsubjectconsent,
    view_subjectconsent,
    "edc_locator.view_historicalsubjectlocator",
    "edc_locator.view_subjectlocator",
    "edc_registration.display_dob",
    "edc_registration.display_firstname",
    "edc_registration.display_identity",
    "edc_registration.display_initials",
    "edc_registration.display_lastname",
    "edc_registration.view_historicalregisteredsubject",
    "edc_registration.view_registeredsubject",
]
