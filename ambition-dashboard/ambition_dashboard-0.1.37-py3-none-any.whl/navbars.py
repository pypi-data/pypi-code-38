from edc_navbar import NavbarItem, site_navbars, Navbar
from edc_review_dashboard.navbars import navbar as review_navbar


no_url_namespace = False  # True if settings.APP_NAME == "ambition_dashboard" else False

navbar = Navbar(name="ambition_dashboard")

navbar.append_item(
    NavbarItem(
        name="screened_subject",
        title="Screening",
        label="Screening",
        fa_icon="fas fa-user-plus",
        codename="edc_navbar.nav_screening_section",
        url_name="screening_listboard_url",
        no_url_namespace=no_url_namespace,
    )
)

navbar.append_item(
    NavbarItem(
        name="consented_subject",
        title="Subjects",
        label="Subjects",
        fa_icon="far fa-user-circle",
        codename="edc_navbar.nav_subject_section",
        url_name="subject_listboard_url",
        no_url_namespace=no_url_namespace,
    )
)

navbar.append_item(
    NavbarItem(
        name="tmg_home",
        label="TMG",
        fa_icon="fas fa-chalkboard-teacher",
        codename="edc_navbar.nav_tmg_section",
        url_name="ambition_dashboard:tmg_home_url",
        no_url_namespace=no_url_namespace,
    )
)

# navbar.append_item(
#     NavbarItem(
#         name="tmg_ae",
#         label="TMG AE",
#         # fa_icon='fas fa-chalkboard-teacher',
#         codename="edc_navbar.nav_tmg_section",
#         url_name="tmg_ae_listboard_url",
#         no_url_namespace=no_url_namespace,
#     )
# )
#
# navbar.append_item(
#     NavbarItem(
#         name="tmg_death",
#         label="TMG Death Reports",
#         # fa_icon='fas fa-chalkboard-teacher',
#         codename="edc_navbar.nav_tmg_section",
#         url_name="tmg_death_listboard_url",
#         no_url_namespace=no_url_namespace,
#     )
# )
#
# navbar.append_item(
#     NavbarItem(
#         name="tmg_summary",
#         label="TMG Summary",
#         # fa_icon='fas fa-chalkboard-teacher',
#         codename="edc_navbar.nav_tmg_section",
#         url_name="tmg_summary_listboard_url",
#         no_url_namespace=no_url_namespace,
#     )
# )

for item in review_navbar.items:
    navbar.append_item(item)


navbar.append_item(
    NavbarItem(
        name="ae_home",
        label="AE",
        codename="edc_navbar.nav_ae_section",
        url_name="ambition_dashboard:ae_home_url",
        no_url_namespace=no_url_namespace,
    )
)


site_navbars.register(navbar)
