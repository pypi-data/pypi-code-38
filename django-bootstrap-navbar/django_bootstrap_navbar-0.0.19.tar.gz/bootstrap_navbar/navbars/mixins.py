from typing import Dict
from django.http import HttpRequest


class BootstrapNavBarViewMixin:
    """Django navbar view mixin which adds the navbar to the context
    and sets the active route based on the request url.
    """

    navbar_class = None

    def get_navbar(self, request: HttpRequest):
        """"""

        if self.navbar_class is None:
            return

        navbar = self.navbar_class(extra_context={"request": request})
        navbar.set_active_navitem()
        return navbar

    def get_context_data(self, **kwargs: Dict) -> Dict:
        """Add the navbar to the view context."""

        context = super().get_context_data(**kwargs)

        if self.navbar_class is not None:
            context["navbar"] = self.get_navbar(self.request)

        return context
