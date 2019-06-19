
from .core import BlogBuilder, FileBuilder
from .core.exceptions import BlogException, PathError, AuthorizationError

from libaloha.cache import RedisCache, CacheConnectionError
from libaloha.django import AlohaView

from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.views.generic import TemplateView

import datetime
import logging
import os
import random
import string

logger = logging.getLogger(__name__)


class BlogFileView(TemplateView):

    EXTENSIONS = ['jpg', 'png', 'pdf', 'gpx']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def head(self, *args, **kwargs):
        """Retourne la date de dernière modification de l'image"""

        response = HttpResponse('')
        return response

        # TODO inch'allah !
        url = kwargs.get('url')
        path = self._get_image_path(url)
        if path:
            response['Last-Modified'] = datetime.datetime.fromtimestamp(
                os.path.getmtime(path)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response

    def get(self, request, *args, **kwargs):

        url = kwargs.get('url', None)
        builder = FileBuilder(settings.BLOG_FOLDER, BlogFileView.EXTENSIONS)

        try:
            file = builder.get(url)
        except FileNotFoundError:
            return HttpResponseNotFound()

        response = HttpResponse(file.content, content_type=file.content_type)
        return response


class BlogGpxView(TemplateView):
    template_name = 'blog/gpx-section.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, gpx, *args, **kwargs):
        logger.debug("Affichage d'un fichier GPX: {}".format(gpx))
        map_id = 'map' + ''.join(random.sample(string.ascii_lowercase, 5))
        context = {
            'map_id': map_id,
            'gpx_url': gpx
        }
        return self.render_to_response(context)


class BlogContentView(AlohaView):
    template_name = 'blog/content.html'

    def __init__(self):
        super().__init__()
        self._contains_gpx = False

    def parse_content_html(self, content):
        """
        Retourne le contenu HTML formaté pour le blog
        :param content:
        :param html:
        :return:
        """

        html = content.content
        soup = BeautifulSoup(html, "html.parser")

        prefix = content.url

        # Si ce n'est pas un fichier d'index, on retire le nom du fichier de l'url
        if not content.path.endswith(settings.BLOG_INDEX_FILE):
            prefix = os.path.split(prefix)[0]

        # On remplace les urls des images pour les faire correspondre
        for img in soup.find_all('img'):
            img_url = os.path.join(prefix, img['src'])
            img['src'] = reverse('blog:file', kwargs={'url': img_url})

        # On recherche les tags GPX pour les remplacer par le contenu
        for p in soup.find_all('p'):
            if p.text.startswith('{{gpx:') and p.text.endswith('}}'):
                gpx_url = reverse('blog:file', kwargs={'url': os.path.join(prefix, p.text[6:-2])})
                tmp = BlogGpxView.as_view()(self.request, gpx_url)
                gpx_section = BeautifulSoup(tmp.rendered_content, "html.parser")
                p.replace_with(gpx_section)
                self._contains_gpx = True

        return str(soup)

    def get_breadcrumb(self, content):
        breadcrumb = []
        parent = content.parent
        while parent:

            parent_title = parent.title
            if not parent.url:
                parent_title = "Home"
            bc = {'url': parent.url, 'title': parent_title}

            parent = parent.parent
            breadcrumb.append(bc)

        breadcrumb.reverse()
        return breadcrumb

    def get(self, request, *args, **kwargs):

        url = kwargs.get('url', '')

        # Récupération du cache
        cache = None
        try:
            cache = RedisCache(prefix="my-blog:")
        except CacheConnectionError:
            logger.warning("Impossible de se connecter au serveur redis")
            cache = None

        # Récupération des groupes
        groups = []
        if request.user.is_authenticated and hasattr(request.user, 'ldap_user'):
            groups = request.user.ldap_user.group_names

        builder = BlogBuilder(
            base_folder=settings.BLOG_FOLDER,
            category_file=settings.BLOG_INDEX_FILE,
            cache=cache,
            groups=groups,
            is_admin=request.user.is_staff
        )

        try:
            content = builder.get(url)

        except BlogException as e:
            logger.error("Recherche de contenu: {}".format(str(e)))

            message = "J'ignore pourquoi vous êtes ici..."
            if isinstance(e, PathError):
                message = "Le contenu demandé n'existe pas."
            elif isinstance(e, AuthorizationError):
                message = "Vous n'avez pas l'autorisation d'atteindre ce contenu."

            return self.redirect_to_error(message)

        self.title = content.title
        content.content = self.parse_content_html(content)

        context = super().get_context_data()
        context['content'] = content
        context['previous_content'] = content.previous
        context['next_content'] = content.next
        context['breadcrumb'] = self.get_breadcrumb(content)
        context['contains_gpx'] = self._contains_gpx
        return self.render_to_response(context)
