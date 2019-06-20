from typing import Union
from urllib.parse import urlparse
from django.template.loader import get_template
from bootstrap_navbar.navbars.base import NavItemBase, NavLinkBase, Href


class Image:
    template_name = "bootstrap_navbar/bootstrap4/image.html"

    def __init__(
        self, *, src: str, class_list: list = None, attrs: dict = None
    ) -> None:
        """Instantiate the class instance."""

        self._src = src
        self._class_set = set(class_list or [])
        self._attrs = attrs or {}

    @property
    def src(self) -> str:
        return self._src

    @property
    def attrs(self) -> dict:
        return self._attrs

    @property
    def class_list(self) -> list:
        return list(self._class_set)

    def get_context_data(self) -> dict:
        return {"src": self.src, "attrs": self.attrs, "class_list": self.class_list}

    def render(self) -> str:
        """Render the image."""

        context = self.get_context_data()
        return get_template(self.template_name).render(context=context)


class Link(NavLinkBase):
    """Anchor tag used for navigation purposes."""

    template_name = "bootstrap_navbar/bootstrap4/link.html"


class ListItem(Link):
    """Anchor tag used for navigation purposes. Note this class is identical to
    Link class except for an additional class which is added in the initialize.
    """

    template_name = "bootstrap_navbar/bootstrap4/link.html"

    def __init__(
        self,
        *,
        text: str,
        href: Union[str, Href] = None,
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: list = None,
        attrs: dict = None,
    ) -> None:
        """Instantiate the class instance."""

        super().__init__(
            text=text,
            href=href,
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        # Insert the appropriate bootstrap classes
        self._class_set.add("nav-item")
        self._class_set.add("nav-link")


class DropDown(NavItemBase):
    """Dropdown navigation menu."""

    template_name = "bootstrap_navbar/bootstrap4/dropdown.html"

    def __init__(
        self,
        *,
        text: str,
        children: list,
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: list = None,
        attrs: dict = None,
    ) -> None:
        """Instantiate the class instance."""

        super().__init__(
            text=text,
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        # Validate the children are of type NavLinkBase and add the appropriate bootstrap classes
        for child in children:
            if not isinstance(child, NavLinkBase):
                raise TypeError(
                    f"unsupported type for child attribute - '{type(child)}'"
                )

            child._class_set.add("dropdown-item")

        self._children = children

    @property
    def href(self) -> str:
        """Return the href of the active link."""

        for child in self.children:
            if child.active is True:
                return child.href

    @property
    def children(self):
        return self._children

    def get_context_data(self) -> dict:
        """Add the dropdown children to the context."""

        context = super().get_context_data()
        context.update({"children": self.children})
        return context


class Brand(NavLinkBase):
    """Bootstrap 4 navbar brand."""

    template_name = "bootstrap_navbar/bootstrap4/brand.html"

    def __init__(
        self,
        *,
        text: str,
        href: Union[str, Href] = None,
        active: bool = False,
        disabled: bool = False,
        active_class: str = "active",
        class_list: list = None,
        attrs: dict = None,
        image: Image = None,
    ) -> None:
        """Instantiate the class instance."""

        super().__init__(
            text=text,
            href=href,
            active=active,
            disabled=disabled,
            active_class=active_class,
            class_list=class_list,
            attrs=attrs,
        )

        self._image = image

    @property
    def image(self):
        return self._image

    def get_context_data(self) -> dict:
        """Add the brand image to the context."""

        context = super().get_context_data()
        context.update({"image": self.image})
        return context


class NavGroup:
    template_name = "bootstrap_navbar/bootstrap4/list.html"

    def __new__(cls):
        """Validate the Meta class."""

        cls._meta = getattr(cls, "Meta", type("Meta", (), {}))

        if "class_list" not in cls._meta.__dict__:
            raise AttributeError("'class_list' is a required Meta class property")

        if "navitems" not in cls._meta.__dict__:
            raise AttributeError("'navitems' is a required Meta class property")

        return super().__new__(cls)

    def __init__(self) -> None:
        """Instantiate the class instance."""

        self._navitems = []
        for _navitem in self._meta.navitems:
            navitem = getattr(self, _navitem, None)

            if navitem is None:
                raise AttributeError(
                    f"'{_navitem}' is declared in the Meta class but does not exist on the '{self.__class__}'"
                )

            self._navitems.append(navitem)

        self._class_set = set(self._meta.class_list)

    @property
    def class_list(self) -> list:
        """Return a list of classes."""

        return list(self._class_set)

    @property
    def navitems(self):
        """Iterate through the navitems."""

        for navitem in self._navitems:
            yield navitem

    def get_context_data(self) -> dict:
        """Generate the navbar context data."""

        return {"navitems": self.navitems, "class_list": self.class_list}

    def render(self) -> str:
        """Render the navigation list."""

        context = self.get_context_data()
        return get_template(self.template_name).render(context=context)


class NavBar:
    template_name = "bootstrap_navbar/bootstrap4/navbar.html"

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Validate the Meta class."""

        cls._meta = getattr(cls, "Meta", type("Meta", (), {}))

        if "class_list" not in cls._meta.__dict__:
            cls._meta.class_list = []

        if "attrs" not in cls._meta.__dict__:
            cls._meta.attrs = {}

        if "brand" not in cls._meta.__dict__:
            cls._meta.brand = None

        if "navgroups" not in cls._meta.__dict__:
            cls._meta.navgroups = []

        return super().__new__(cls)

    def __init__(self, extra_context: dict = None):
        """Instantiate the class instance."""

        self._class_set = set(self._meta.class_list)
        self._attrs = self._meta.attrs
        self._navgroups = []

        for _navgroup in self._meta.navgroups:
            navgroup = getattr(self, _navgroup, None)

            if navgroup is None:
                raise ValueError(
                    f"'{_navgroup}' is declared in the Meta class but does not exist on the '{self.__class__}'"
                )

            self._navgroups.append(navgroup)

        self._brand = getattr(self._meta, "brand", None)
        self._extra_context = extra_context or {}

    @property
    def brand(self):
        return self._brand

    @property
    def navgroups(self):
        return self._navgroups

    @property
    def class_list(self) -> list:
        return list(self._class_set)

    @property
    def attrs(self):
        return self._attrs

    @property
    def active_navitem(self) -> NavLinkBase:
        """Return the active navitem."""

        try:
            return next(filter(lambda x: x.active is True, self.navitems))
        except StopIteration:
            return

    @property
    def navitems(self) -> list:
        """Return a list of all the navitems."""

        for navgroup in self.navgroups:
            yield from navgroup.navitems

    @property
    def extra_context(self) -> dict:
        return self._extra_context

    def _set_active_navitem_dispatch(self, navitem: NavLinkBase, path: str) -> bool:
        """Dispatch to the appropriate function based on the navitem type."""

        if isinstance(navitem, DropDown):
            return self._set_active_navitem_dropdown(navitem, path)
        else:
            return self._set_active_navitem_link(navitem, path)

    def _set_active_navitem_link(self, navitem: ListItem, path: str):
        """Set the navitem to active if the current path matches the href."""

        components = urlparse(navitem.href)
        navitem.active = components.path == path
        return navitem.active

    def _set_active_navitem_dropdown(self, dropdown: DropDown, path: str):
        """Set the dropdown to active if the current path matches one of the navitems href."""

        for navitem in dropdown.children:
            components = urlparse(navitem.href)
            navitem.active = components.path == path
            navitem.active = components.path == path

            if navitem.active:
                dropdown.active = True
                return True

        return False

    def set_active_navitem(self) -> None:
        """Set the active flag of the active navitem."""

        request = self.extra_context.get("request", None)

        if request is None:
            raise AttributeError(
                "navbar requires the request instance to set the active navitem"
            )

        for navitem in self.navitems:
            navitem.active = False

            if isinstance(navitem, DropDown):
                for child in navitem.children:
                    child.active = False

        for navitem in self.navitems:
            if self._set_active_navitem_dispatch(navitem, request.path) is True:
                return

    def get_context_data(self) -> dict:
        """Generate the navbar context data."""

        return {
            "brand": self.brand,
            "navgroups": self.navgroups,
            "attrs": self.attrs,
            "class_list": self.class_list,
        }

    def render(self) -> str:
        """Render the navbar."""

        context = self.get_context_data()
        context.update(self.extra_context)
        return get_template(self.template_name).render(context=context)
