from django.contrib import admin

from .models import Faq, Collective, Testimony, Regionevent, Typeevent,Locationevent, Event, Client, Howareyou, Howhelp, Workwish, Contact

admin.site.register(Faq)
admin.site.register(Collective)
admin.site.register(Testimony)
admin.site.register(Regionevent)
admin.site.register(Typeevent)
admin.site.register(Event)
admin.site.register(Locationevent)
admin.site.register(Client)
admin.site.register(Howareyou)
admin.site.register(Howhelp)
admin.site.register(Workwish)
admin.site.register(Contact)