from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.logo.browser.logo_base_viewlet import LogoBaseViewlet


class LogoViewlet(LogoBaseViewlet):

    index = ViewPageTemplateFile('logo_viewlet.pt')
