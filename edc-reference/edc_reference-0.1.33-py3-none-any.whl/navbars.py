from edc_navbar import Navbar, NavbarItem, site_navbars


navbar = Navbar(name="edc_reference")

navbar.append_item(
    NavbarItem(
        name="reference",
        title="reference",
        label="reference",
        url_name="edc_reference:home_url",
        codename="edc_navbar.nav_reference",
    )
)

site_navbars.register(navbar)
