# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina_mailer.interfaces import IMailer
from guillotina.component import provide_utility
from guillotina.utils import import_class


app_settings = {
    "mailer": {
        "default_sender": "foo@bar.com",
        "endpoints": {
            "default": {
                "type": "smtp",
                "host": "localhost",
                "port": 25
            }
        },
        "debug": False,
        "utility": "guillotina_mailer.utility.MailerUtility",
        "use_html2text": True,
        "domain": None
    }
}


configure.permission(id="mailer.SendMail", title="Request subscription")
configure.grant(permission="mailer.SendMail", role="guillotina.ContainerAdmin")


def includeme(root, settings):
    factory = import_class(
        settings.get('mailer', {}).get('utility',
                                       app_settings['mailer']['utility']))
    utility = factory()
    provide_utility(utility, IMailer)

    configure.scan('guillotina_mailer.api')
    configure.scan('guillotina_mailer.utility')
