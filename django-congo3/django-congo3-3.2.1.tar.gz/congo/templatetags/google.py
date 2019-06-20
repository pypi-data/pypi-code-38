# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.templatetags.common import form_iriencode
from django.template import Library

register = Library()

@register.simple_tag
def google_maps(mode, **kwargs):
    """
    Tag zwraca mapkę google maps.
    
    {% google_maps mode="street_view" %}
    {% google_maps mode="street_view_img" %}
    {% google_maps mode="directions" %}
    {% google_maps mode="place" %}
    {% google_maps mode="place_img" %}
    {% google_maps mode="external" %}
    {% google_maps mode="external-directions" %}
    """

    # https://console.developers.google.com/project/notional-grove-89813/apiui/credential
    key = settings.CONGO_GOOGLE_BROWSER_API_KEY

    if mode == "street_view":
        # https://www.google.pl/maps/@52.2021098,20.5612702,3a,90y,103.45h,85.34t/data=!3m7!1e1!3m5!1sgfByKVyrwy0AAAQo8YZlqQ!2e0!3e2!7i13312!8i6656!6m1!1e1
        # location=52.2021098,20.5612702

        location = kwargs.get('location', '52.200891,20.560264')
        # kierunek w płaszyźnie poziomej: +/- 180
        heading = kwargs.get('heading', 60)
        # odchylenie od poziomu: +/- 90
        pitch = kwargs.get('pitch', 5)
        # zumm: 15 - 90
        fov = kwargs.get('fov', 65)
        return "https://www.google.com/maps/embed/v1/streetview?key=%s&location=%s&heading=%s&pitch=%s&fov=%s" % (key, location, heading, pitch, fov)
    elif mode == "street_view_img":
        location = kwargs.get('location', '52.200891,20.560264')
        heading = kwargs.get('heading', 60)
        pitch = kwargs.get('pitch', 5)
        scale = kwargs.get('scale', 2)
        # max size: 640x640
        size = kwargs.get('size', '640x640')
        return "https://maps.googleapis.com/maps/api/streetview?key=%s&location=%s&heading=%s&pitch=%s&scale=%s&size=%s" % (key, location, heading, pitch, scale, size)
    elif mode == "directions":
        origin = kwargs.get('origin', 'Warszawa, Polska')
        destination = kwargs.get('destination', 'Faktor, Piorunów 13, 05-870 Błonie, Polska')
        avoid = kwargs.get('avoid', 'tolls')
        return "https://www.google.com/maps/embed/v1/directions?key=%s&origin=%s&destination=%s&avoid=%s" % (key, form_iriencode(origin), form_iriencode(destination), form_iriencode(avoid))
    elif mode == "place":
        q = kwargs.get('q', 'Faktor, Piorunów 13, 05-870 Błonie, Polska')
        zoom = kwargs.get('zoom', '10')
        return "https://www.google.com/maps/embed/v1/place?key=%s&q=%s&zoom=%s" % (key, form_iriencode(q), zoom)
    elif mode == "place_img":
        center = kwargs.get('center', '52.200891,20.560264')
        # max size: 640x640
        size = kwargs.get('size', '640x640')
        zoom = kwargs.get('zoom', '10')
        markers = kwargs.get('markers', 'color:red%7C52.200891,20.560264')
        return "https://maps.googleapis.com/maps/api/staticmap?key=%s&center=%s&zoom=%s&markers=%s&size=%s" % (key, form_iriencode(center), zoom, markers, size)
    elif mode == "external":
        location = kwargs.get('location', '52.200891,20.560264')
        zoom = kwargs.get('zoom', '10')
        place_id = kwargs.get('place_id', '3945958479054158299')
        return "https://maps.google.com/maps?ll=%s&z=%s&cid=%s" % (location, zoom, place_id)
    elif mode == "external-directions":
        origin = kwargs.get('origin', 'Warsaw+Poland')
        destination = kwargs.get('destination', 'Faktor,+Piorun%C3%B3w+13,+05-870+B%C5%82onie,+Polska')
        return "https://www.google.com/maps/dir/%s/%s/" % (origin, destination)
    return ""
