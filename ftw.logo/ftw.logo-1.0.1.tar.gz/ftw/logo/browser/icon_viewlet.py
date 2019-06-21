from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.logo.browser.logo_base_viewlet import LogoBaseViewlet


class IconViewlet(LogoBaseViewlet):

    index = ViewPageTemplateFile('icon_viewlet.pt')
