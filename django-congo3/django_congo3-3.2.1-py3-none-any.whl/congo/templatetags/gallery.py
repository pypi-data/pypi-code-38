# -*- coding: utf-8 -*-
from congo.gallery.classes import BlankImage
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


def _photo_url(photo, **kwargs):
    # width (int)
    try:
        width = int(kwargs.get('width'))
    except (ValueError, TypeError):
        width = None

    # height (int)
    try:
        height = int(kwargs.get('height'))
    except (ValueError, TypeError):
        height = None

    # size (int)
    try:
        width = int(kwargs.get('size'))
        height = width
    except (ValueError, TypeError):
        pass

    # crop (bool)
    crop = bool(kwargs.get('crop'))

    html = None
    if photo and getattr(photo, 'image'):
        html = photo.image.get_url(width, height, crop)
    if not html:
        html = BlankImage().get_url(width, height)
    return mark_safe(html)

@register.simple_tag
def blank_photo_url(**kwargs):
    """
    Tag zwraca url do pustego zdjęcia.
    
    {% blank_photo_url width=100 height=100 crop=False %}
    {% blank_photo_url size=100 crop=True %}
    """

    return _photo_url(None, **kwargs)

def _render_photo(photo, **kwargs):
    # width (int)
    try:
        width = int(kwargs.get('width'))
    except (ValueError, TypeError):
        width = None

    # height (int)
    try:
        height = int(kwargs.get('height'))
    except (ValueError, TypeError):
        height = None

    # size (int)
    try:
        width = int(kwargs.get('size'))
        height = width
    except (ValueError, TypeError):
        pass

    html = None
    if photo and hasattr(photo, 'image') and photo.image:
        html = photo.image.render(width, height, **kwargs)
    if not html:
        html = BlankImage().render(width, height, **kwargs)
    return mark_safe(html)

def _photos(photo_list, **kwargs):
    # title (string)
    title = kwargs.get('title', '')

    # label (string)
    label = kwargs.get('note', '')

    # add_url (bool)
    add_url = bool(kwargs.get('add_url', False))

    # add_blank (bool)
    add_blank = bool(kwargs.get('add_blank', True))

    # as_gallery (bool)
    as_gallery = bool(kwargs.get('as_gallery', None))

    # thumbnail (bool)
    thumbnail = bool(kwargs.get('thumbnail', True))

    # @md do czego to?
    # md -> na ta chwile jedynie uzywane w nestedach w bomm. Sluzy do podawania wielkości obrazu w colorbox

    # zoom size (int)
    max_width = kwargs.get('zoom_size')
    max_height = kwargs.get('zoom_size')

    def render(photo):
        if photo:
            _title = title or photo.title or ""
            image_url = ""

            if label:
                image_label = """<span class="note">%s</span>""" % label
            else:
                image_label = ""

            if add_url:
                image_url = photo.image.get_url(max_width, max_height)

            if image_url:
                image_html = _render_photo(photo, **kwargs)
                return mark_safe("""<div class="thumbnail-wrapper"><a href="%s" title="%s" class="%s colorbox">%s%s</a></div>""" % (image_url, _title, 'thumbnail' if thumbnail else '', image_html, image_label))
            else:
                kwargs['alt_text'] = _title
                image_html = _render_photo(photo, **kwargs)
                return mark_safe("""<div class="thumbnail-wrapper">%s%s</div>""" % (image_html, image_label))
        else:
            kwargs['alt_text'] = title
            image_html = _render_photo(photo, **kwargs)
            return mark_safe("""<div class="thumbnail-wrapper">%s</div>""" % (image_html))

    html = ""
    if as_gallery or len(photo_list) > 1:
        html = """<div class="
        thumbnail-gallery">%s</div>""" % ''.join([render(photo) for photo in photo_list])
    elif len(photo_list) == 1:
        html = render(photo_list[0])
    elif add_blank:
        # if no photos add blank image
        html = render(None)
    return mark_safe(html)

@register.simple_tag
def blank_photo(**kwargs):
    return _photos([], **kwargs)

def _video(video_id, model, **kwargs):
    # popup
    popup = bool(kwargs.get('popup', False))

    # autoplay (bool)
    autoplay = bool(kwargs.get('autoplay', popup))

    # title (string)
    title = kwargs.get('title', "")

    # width (int)
    try:
        width = int(kwargs.get('width'))
    except (ValueError, TypeError):
        width = 200 if popup else None

    # height (int)
    try:
        height = int(kwargs.get('height'))
    except (ValueError, TypeError):
        height = width if popup else None

    try:
        video = model.objects.get(id = int(video_id))
        if popup:
            title = title or video.title or ""
            kwargs['css_class'] = 'img-responsive'

            html = mark_safe("""<div class="thumbnail-wrapper"><a href="%s" class="thumbnail popup" title="%s">%s</a></div>""" % (video.get_url(autoplay), title, video.image.render(width, height, **kwargs)))
        else:
            html = mark_safe("""<div class="thumbnail"><div class="video-wrapper">%s</div></div>""" % video.render(width, height, autoplay))
    except (ValueError, TypeError, ObjectDoesNotExist):
        html = ""

    return mark_safe(html)
