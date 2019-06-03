"""Checkbox Renderer class
"""
import logging

from core_parser_app.tools.parser.renderer.list import ListRenderer

logger = logging.getLogger(__name__)


class CheckboxRenderer(ListRenderer):
    """Checkbox renderer, makes elements selectable
    """

    def _render_input(self, element):
        """Renders a selectable element

        Args:
            element:

        Returns:

        """
        data = {
            'id': element.pk,
            'selected': True if element.value == 'true' else False,
        }
        return self._load_template('checkbox', data)

    def render_restriction(self, element):
        """Renders a selectable element

        Args:
            element:

        Returns:

        """
        data = {
            'id': element.pk,
            'selected': True if element.value == 'true' else False,
        }
        return self._load_template('checkbox', data)
