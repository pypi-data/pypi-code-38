
from django.http import HttpResponse
import qrcode
from django.views.generic import View


class QRCode(View):

    def get(self, request):
        img = qrcode.make('https://www.frontzdrilling.com')
        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')
        return response