from typing import Dict
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from bootstrap_navbar.navbars import bootstrap4

import pytest


User = get_user_model()


class NavGroup(bootstrap4.NavGroup):
    home = bootstrap4.ListItem(text="Home", href="/")

    class Meta:
        navitems = ("home",)
        class_list = ("mr-auto",)


class NavBar(bootstrap4.NavBar):
    navigation = NavGroup()

    class Meta:
        navgroups = ("navigation",)
        class_list = ("navbar-dark",)


@pytest.fixture
def user():
    user = User.objects.create(username="test")
    user.set_password("test")
    return user


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def navbar_class():
    return NavBar


@pytest.fixture
def navbar():
    return NavBar()


@pytest.fixture
def base_attrs() -> Dict:
    return {
        "text": "testing",
        "active": True,
        "disabled": False,
        "active_class": "active",
        "class_list": ["my-class"],
        "attrs": {"style": "backgroud-color: blue;"},
    }


@pytest.fixture
def link_attrs(base_attrs: Dict) -> Dict:
    base_attrs_copy = base_attrs.copy()
    base_attrs_copy["href"] = "/"
    return base_attrs_copy


@pytest.fixture
def dropdown_attrs(base_attrs: Dict) -> Dict:
    base_attrs_copy = base_attrs.copy()
    base_attrs_copy["children"] = [bootstrap4.Link(text="link", href="/")]
    return base_attrs_copy
