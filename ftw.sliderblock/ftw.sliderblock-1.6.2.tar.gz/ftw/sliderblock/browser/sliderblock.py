from Acquisition._Acquisition import aq_inner
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.images.cropping.behaviors import IImageCropping
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.slider.browser.slider import SliderView
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SliderBlockView(BaseBlock, SliderView):
    template = ViewPageTemplateFile('templates/sliderblock.pt')

    def can_add(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission('ftw.sliderblock: Add SliderBlock',
                                           context)
        return bool(permission)

    def get_template_data(self):
        data = []
        for pane in self.panes():
            data.append({
                'uid': pane.UID(),
                'title': pane.title,
                'show_title': pane.show_title,
                'title_css_classes': self.get_title_css_classes(pane),
                'text': pane.text,
                'show_pane_caption': pane.show_title or pane.text,
                'image_tag': self.get_image_tag(pane),
                'link_url': self.get_link_url(pane),
                'obj': pane,
            })
        return data

    def get_title_css_classes(self, pane):
        """
        Returns the css classes of the pane title. Internal links
        take precedence over external links.
        """
        title_css_classes = ['documentFirstHeading', 'title']
        if not pane.link and pane.external_url:
            title_css_classes.append('external-link')
        return ' '.join(title_css_classes)

    def get_image_tag(self, pane):
        scaling = pane.restrictedTraverse('@@images')
        direction = self.context.crop_image and 'down' or 'up'
        field_name = 'image'
        if IImageCropping.providedBy(pane) and pane.cropped_image:
            field_name = 'cropped_image'

        scale = scaling.scale(field_name, scale='sliderblock', direction=direction)

        alttext = u''
        if hasattr(pane, 'image_alt_text'):
            alttext = pane.image_alt_text if pane.image_alt_text else u''

        return scale.tag(css_class='headerImage', alt=alttext, title='')

    def get_link_url(self, pane):
        """
        Returns the link url of the pane. Internal links
        take precedence over external url.
        """
        internal_link = pane.link
        if internal_link:
            return '{0}{1}'.format(
                api.portal.get().absolute_url(),
                internal_link.startswith('/') and internal_link or '/' + internal_link
            )

        return pane.external_url or ''

    def show_limit_indicator(self):
        return self.can_add()
