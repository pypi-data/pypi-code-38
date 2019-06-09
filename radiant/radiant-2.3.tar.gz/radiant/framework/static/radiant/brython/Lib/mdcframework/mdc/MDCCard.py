"""
Brython MDCComponent: MDCCard
=============================


"""

from .core import MDCTemplate
from .MDCButton import MDCButton, MDCIconToggle

########################################################################


class MDCCard(MDCTemplate):
    """"""

    NAME = 'card', 'MDCCcard'

    MDC_optionals = {

        'outlined': 'mdc-card--outlined',
        'square': 'mdc-card__media--square',
        '_16_9': 'mdc-card__media--16-9',
        'full_bleed': 'mdc-card__actions--full-bleed',
        "primary_action": "mdc-card__primary-action",

    }

    # ----------------------------------------------------------------------
    def __new__(self, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
        <div class="mdc-card {outlined}">
          <div class="mdc-card__media {square} {_16_9}">
            <div class="mdc-card__media-content"></div>
          </div>

          <div class="{primary_action} radiant-content"></div>

          <div class="mdc-card__actions {full_bleed}">

            <div class="mdc-card__action-buttons">
            </div>

            <div class="mdc-card__action-icons">
            </div>

          </div>
        </div>
        """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'actions':
            return self.element.select('.mdc-card__actions')[0]

        elif name is 'content':
            return self.element.select('.radiant-content')[0]

        elif name is 'media':
            return self.element.select('.mdc-card__media')[0]

        elif name is 'media_content':
            return self.element.select('.mdc-card__media-content')[0]

        elif name is 'action_buttons':
            return self.element.select('.mdc-card__action-buttons')[0]

        elif name is 'action_icons':
            return self.element.select('.mdc-card__action-icons')[0]

    # ----------------------------------------------------------------------
    @classmethod
    def add_action_button(cls, element, *args, **kwargs):
        """"""
        button = MDCButton(*args, **kwargs)
        button.class_name += ' mdc-card__action mdc-card__action--button'
        cls['action_buttons'] <= button

        return button

    # ----------------------------------------------------------------------
    @classmethod
    def add_action_icontoggle(cls, element, *args, **kwargs):
        """"""
        button = MDCIconToggle(*args, **kwargs)
        button.class_name += ' mdc-card__action mdc-card__action--icon'
        cls['action_icons'] <= button

        return button

    # ----------------------------------------------------------------------
    @classmethod
    def add_action_icon(cls, element, icon, *args, **kwargs):
        """"""
        button = MDCButton(icon=icon, *args, **kwargs)
        button.class_name += ' mdc-card__action mdc-card__action--icon'
        cls['action_icons'] <= button

        return button
