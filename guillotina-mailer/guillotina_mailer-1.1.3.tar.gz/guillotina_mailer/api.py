from guillotina import configure
from guillotina.api.service import Service
from guillotina.response import Response
from guillotina.component import queryUtility
from guillotina.interfaces import IContainer
from guillotina_mailer.interfaces import IMailer


@configure.service(context=IContainer, name='@mailer', method="POST",
                   permission="mailer.SendMail")
class SendMail(Service):

    async def __call__(self):
        data = await self.request.json()
        mailer = queryUtility(IMailer)
        await mailer.send(**data)
        return Response(content={
            'messages_sent': 1
        }, status=200)
