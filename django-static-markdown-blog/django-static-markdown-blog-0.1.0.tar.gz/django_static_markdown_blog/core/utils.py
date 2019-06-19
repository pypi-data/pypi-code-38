
import os
import json
import logging
import datetime

logger = logging.getLogger(__name__)


class BlogContentConverter:

    @staticmethod
    def content_to_json(content, date_format='%Y%m%d-%H%M%S'):
        """
        Convertit un contenu en JSON
        :param content:
        :param date_format:
        :return:
        """
        values = {
            'num': content.num,
            'title': content.title,
            'content': content.content,
            'icon': content.icon,
            'date': datetime.datetime.strftime(content.date, date_format),
        }

        if content.groups:
            values['groups'] = ','.join(content.groups)

        if content.parent:
            values['parent'] = content.parent.path

        return json.dumps(values)

    @staticmethod
    def load_json_in_content(content, data, date_format='%Y%m%d-%H%M%S'):
        """
        Charge le contenu d'un JSON dans un contenu
        :param content:
        :param data:
        :param date_format:
        :return:
        """
        values = json.loads(data)

        content.num = values['num']
        content.title = values['title']
        content.content = values['content']
        content.icon = values['icon']
        content.date = datetime.datetime.strptime(values['date'], date_format)

        if 'groups' in values and values['groups']:
            content.groups = values['groups'].split(',')


class BlogContentCache:

    def __init__(self, content, cache):
        self._content = content
        self._cache = cache

        self._date_format = '%Y%m%d-%H%M%S'

        self._key = "content:{}".format(content.url)
        self._key_date = "last_update:{}".format(content.url)

    def _get_datetime_from_file(self):
        """
        Récupère la date du contenu depuis le fichier
        :return:
        """
        if not os.path.isfile(self._content.path):
            logger.error("Tentative d'enregistrement en cache d'un contenu sans fichier associé: {}".format(
                self._content.url))
            raise FileNotFoundError(self._content.path)

        ts = os.path.getmtime(self._content.path)
        date = datetime.datetime.fromtimestamp(ts)
        return date.replace(microsecond=0)

    def _get_datetime_from_cache(self):
        """
        Récupère la date du contenu depuis le cache
        :return:
        """
        if not self._cache:
            return

        if self._cache.exists(self._key_date):
            str_date = str(self._cache.get(self._key_date))
            return datetime.datetime.strptime(str_date, self._date_format)

    def need_update(self):

        # Si pas de cache, on force la mise à jour
        if not self._cache:
            return True

        # Si une clé n'existe pas en cache, on force la mise à jour
        if not self._cache.exists(self._key) or not self._cache.exists(self._key_date):
            return True

        file_date = self._get_datetime_from_file()
        cache_date = self._get_datetime_from_cache()

        # Si on ne retrouve pas de date en cache, on force la mise à jour
        if not cache_date:
            return True

        # On force la mise à jour si le fichier est plus récent que le cache
        return file_date > cache_date

    @property
    def content(self):

        data = self._cache.get(self._key)
        BlogContentConverter.load_json_in_content(self._content, data)

        return self._content

    def save(self):
        if not self._cache:
            return

        # Enregistrement des données
        data = BlogContentConverter.content_to_json(self._content)
        self._cache.set(self._key, data)

        # Enregistrement de la date de dernière mise à jour
        str_date = self._get_datetime_from_file().strftime(self._date_format)
        self._cache.set(self._key_date, str_date)