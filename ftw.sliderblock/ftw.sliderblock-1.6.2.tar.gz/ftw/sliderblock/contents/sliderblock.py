from collections import OrderedDict
from ftw.simplelayout import _ as SLPMF
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.sliderblock import _
from ftw.sliderblock.contents.constraints import validate_slick_config
from ftw.sliderblock.contents.interfaces import ISliderBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements


def slick_config_default_value():
    settings = getUtility(IRegistry)
    return settings.get(
        'ftw.sliderblock.default_slick_config',
        u'{"autoplay": true, "autoplaySpeed": 2000}'
    )


class ISliderBlockSchema(form.Schema):
    """Slider block for simplelayout
    """

    title = schema.TextLine(
        title=_(u'sliderblock_title_label', default=u'Title'),
        required=True,
    )

    show_title = schema.Bool(
        title=_(u'sliderblock_show_title_label', default=u'Show title'),
        default=True,
        required=False,
    )

    crop_image = schema.Bool(
        title=_(u'sliderblock_crop_image_label',
                default=u'Crop and scale images'),
        description=_(u'help_text_crop_image',
                      default=u'Crop and scale images to a predefined ratio'),
        default=True,
        required=False,
        missing_value=True
    )

    slick_config = schema.Text(
        title=_(u'sliderblock_slick_config_label', default=u'Configuration'),
        description=_(u'sliderblock_slick_config_description',
                      default=u'See http://kenwheeler.github.io/slick/'),
        required=False,
        defaultFactory=slick_config_default_value,
        constraint=validate_slick_config,
    )

    form.order_before(title='*')

alsoProvides(ISliderBlockSchema, IFormFieldProvider)


class SliderBlock(Container):
    implements(ISliderBlock)


class SliderBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict(
            [
                ('upload', {
                    'class': 'upload icon-image-upload',
                    'title': translate(
                        SLPMF(u'label_upload', default=u'Upload'),
                        context=self.request),
                    'href': './sl-ajax-upload-block-view'
                }),

                ('folderContents', {
                    'class': 'icon-folder-contents redirect',
                    'title': translate(
                        _(u'label_show_folder_contents',
                          default=u'Show folder contents'),
                        context=self.request),
                    'href': '/folder_contents'}),
            ]
        )
