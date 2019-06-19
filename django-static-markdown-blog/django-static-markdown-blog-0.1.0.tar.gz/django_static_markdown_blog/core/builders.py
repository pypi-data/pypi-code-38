
import os
import locale
import logging
import datetime
from pathlib import Path

from libaloha.cache import AbstractCache
from libaloha.markdown import MarkdownFileReader, MarkdownFile

from .exceptions import PathError, AuthorizationError
from .models import BlogContent, BlogFile
from .utils import BlogContentCache

logger = logging.getLogger(__name__)

# Liste des caractères qui ne doivent pas être remplacés dans l'url
USEFUL_CHARS_IN_PATH = ['/']


class AbstractBuilder:

    def __init__(self, base_folder):

        # Vérifie que le répertoire existe
        if not os.path.isdir(base_folder):
            logger.error("FileBuilder: Répertoire introuvable: {}".format(base_folder))
            raise PathError(base_folder)

        self._base_folder = base_folder


class FileBuilder(AbstractBuilder):

    def __init__(self, base_folder, extensions_autorisees=None):
        super().__init__(base_folder)

        self._extensions_autorisees = extensions_autorisees or []
        self._image_path = ""
        self._image_extension = ""

    def get(self, url):

        path = self._get_image_path(url)
        if not path:
            raise PathError(path)

        file = BlogFile(url, path)
        file.content = open(path, 'rb')
        file.content_type = self._get_content_type()

        return file

    def _get_content_type(self):
        result = "text/plain"

        ext = self._image_extension.lower()
        if ext == 'jpg':
            result = "image/jpeg"
        elif ext == 'png':
            result = "image/png"
        elif ext == 'pdf':
            result = "application/pdf"

        return result

    def _get_image_path(self, url):

        if self._image_path:
            return self._image_path

        if not url:
            return None

        # Vérifie si le chemin existe
        path = os.path.join(self._base_folder, url)
        if not os.path.isfile(path):
            logger.error("File not found: {}".format(path))
            return None

        # Vérifie que l'extension est autorisée
        extension = extension = Path(path).suffix[1:]
        if not extension.lower() in self._extensions_autorisees:
            logger.error("Extension not allowed: {}".format(extension))
            return None

        self._image_path = path
        self._image_extension = extension

        return self._image_path


class BlogBuilder(AbstractBuilder):

    def __init__(self, base_folder, category_file, cache=None, groups=None, is_admin=False):
        super().__init__(base_folder)
        self._category_file = category_file
        self._groups = groups or []
        self._is_admin = is_admin

        # Construction du blog
        self.content = None
        self.blog = self.construire(self._base_folder, parent=None)

        self._cache = None
        if cache and isinstance(cache, AbstractCache):
            self._cache = cache

    def get(self, url=None):

        self.content = None
        path = self._get_path(url)

        logger.debug("TEST:\n  URL={}\n  PATH={}".format(url, path))

        self.content = self.get_content(path)

        # si on n'a pas trouvé
        if not self.content:
            logger.error("Contenu introuvable: {}".format(path))
            raise PathError(path)

        # on charge les contenus nécessaires
        self.charger_contenu(self.content)

        # si on n'a pas accès au contenu
        if not self.verifier_groupes(self.content):
            logger.error("Contenu inaccessible: {}".format(path))
            raise AuthorizationError(self.content)

        previous_locale = locale.getlocale(locale.LC_COLLATE)
        locale.setlocale(locale.LC_COLLATE, 'fr_FR.UTF-8')
        self.traiter_enfants()
        self.traiter_ancetres()
        locale.setlocale(locale.LC_COLLATE, previous_locale)

        return self.content

    @property
    def markdown_extension(self):
        return MarkdownFile.EXTENSION

    def _add_extension(self, value):
        """
        Add extension to some value
        :param value:
        :return:
        """
        result = value
        if not result.endswith(self.markdown_extension):
            result += self.markdown_extension
        return result

    def _remove_extension(self, value):
        """
        Remove extension to some value
        :param value:
        :return:
        """
        result = value
        if result.endswith(self.markdown_extension):
            result = result[:0-len(self.markdown_extension)]
        return result

    def _clean_url(self, url):
        """
        Retourne une URL nettoyée
        :param url:
        :return:
        """
        if not url:
            return ''

        result = url
        # On retire les slashs en début d'url
        while result.startswith('/'):
            result = result[1:]

        return result

    def _clean_path(self, path):
        """
        Retourne un chemin nettoyé
        :param path:
        :return:
        """

        if not path:
            return None

        result = path
        # On retire les slashs en fin de chemin
        while result.endswith('/'):
            result = result[:-1]

        return result

    def _get_url(self, path):
        """
        Retourne l'url d'un contenu à partir de son chemin
        :param path:    Chemin du contenu
        :return:        URL du contenu
        """

        # On retire le nom du fichier de catégorie s'il existe
        # (on ajoute le slash pour être sûr de ne pas traiter d'autres fichiers)
        tmp = '/' + self._category_file
        if path.endswith(tmp):
            path = path[:0 - len(self._category_file)]

        # On retire l'extension
        path = self._remove_extension(path)

        # On transforme en url en retirant la base du répertoire
        url = path.replace(self._base_folder, '')

        return self._clean_url(url)

    def _get_path(self, url):
        """
        Retourne le chemin d'un contenu à partir de son url
        :param url:     URL du contenu
        :return:        Chemin du contenu
        """

        if not url or url == '/':
            url = ''

        path = os.path.join(self._base_folder, url)

        tmp = self._add_extension(path)
        if os.path.isfile(tmp):
            path = tmp
        elif os.path.isdir(path):
            path = os.path.join(path, self._category_file)
        else:
            path = None

        return self._clean_path(path)

    def get_content(self, path, parent=None):
        """
        Récupère un contenu grâce à son url
        :param path:
        :return:
        """

        if not parent:
            parent = self.blog

        if parent.path == path:
            return parent

        for child in parent.children:
            content = self.get_content(path, child)
            if content:
                return content

    def traiter_enfants(self):
        # traitement des enfants
        if self.content.children:

            # chargement des enfants
            for child in self.content.children:

                for c in child.children:
                    self.charger_contenu(c)

                self.charger_contenu(child)
                self.trier_contenu(child)

            self.trier_contenu(self.content)

    def traiter_ancetres(self):
        # traitement des ancêtres
        if self.content.parent:

            # chargement des ancêtres
            parent = self.content.parent
            while parent:
                self.charger_contenu(parent)

                # si on n'a pas accès au parent, on dégage
                if not self.verifier_groupes(parent):
                    logger.error("Contenu inaccessible: {}".format(parent.path))
                    raise AuthorizationError(parent)

                parent = parent.parent

            # chargement et tri des enfants du parent
            # uniquement si on est dans un fichier
            # (on ajoute le slash pour être sûr de ne pas traiter d'autres fichiers)
            tmp = '/' + self._category_file
            if self.content.is_file and not self.content.path.endswith(tmp):

                for child in self.content.parent.children:
                    self.charger_contenu(child)
                self.trier_contenu(self.content.parent)

                # chargement des enfants du parent
                prev = None
                next = None
                tmp_prev = None
                flag_next = False

                for child in self.content.parent.children:

                    # on ne veut pas afficher les répertoires comme précédent/suivant
                    if child.children:
                        continue

                    if flag_next:
                        next = child
                        flag_next = False

                    if self.content.path == child.path:
                        prev = tmp_prev
                        flag_next = True

                    tmp_prev = child

                self.content.previous = prev
                self.content.next = next

    def charger_contenu(self, content):
        """
        Charge le contenu passé en paramètre
        :param content:
        :return:
        """

        # Ne rien faire si le contenu est déjà chargé
        if content.is_loaded:
            return

        # Traitement des répertoires contenant des enfants
        if not content.is_file and content.children:
            dir_name = os.path.dirname(content.path)
            content.title = str(os.path.split(dir_name)[-1]).capitalize()
            content.is_loaded = True
            return

        # Lire le contenu dans le cache si nécessaire
        cache_content = BlogContentCache(content, self._cache)
        if not cache_content.need_update():
            logger.debug("load content from cache {}".format(content.url))
            content = cache_content.content
            content.is_loaded = True
            return

        logger.debug("load content from file {}".format(content.path))
        md = MarkdownFileReader(content.path).get()

        # Update content from markdown file
        content.content = md.html
        try:
            content.num = int(md.get_metadata('num', 50000))
        except ValueError:
            content.num = 0

        content.icon = md.get_metadata('icon', None)
        content.title = md.get_metadata('title', content.title)

        groups = md.get_metadata('groups', None)
        if groups:
            groups = groups.replace(',', '').split()
            logger.debug("{}: groupes -> {}".format(content.url, groups))
            content.groups = groups

        # Récupère la date à partir des métadonnées MD ou bien du fichier
        content.date = datetime.datetime.fromtimestamp(os.path.getmtime(md.path))
        if 'date' in md.metadata:
            content.date = datetime.datetime.strptime(md.get_metadata('date'), '%d/%m/%Y')

        content.is_loaded = True

        # Save content in cache
        cache_content.save()

    def trier_contenu(self, content):
        """
        Trie un contenu s'il a des enfants
        :param content:
        :return:
        """
        if content.children:

            # On retire tous les contenus non chargés
            content.children[:] = [x for x in content.children if x.is_loaded and self.verifier_groupes(x)]
            if not content.children:
                content.is_loaded = self.verifier_groupes(content)
                return

            # On met à jour la date si nécessaire
            max_date = max(content.children, key=lambda x: x.date or datetime.datetime(1990, 1, 1)).date

            # On met à jour la date du répertoire si nécessaire
            if not content.date or content.date < max_date:
                content.date = max_date

            # On trie en deux fois les enfants
            content.children.sort(key=lambda x: locale.strxfrm(x.title))
            content.children.sort(key=lambda x: x.num)

    def verifier_groupes(self, content):
        """
        Vérifie le groupe du contenu passé en paramètre
        :param content:
        :return:
        """

        if not content.groups or self._is_admin:
            return True

        if not self._groups:
            logger.debug("Accès interdit à {}".format(content.url))
            return False

        for grp in self._groups:
            if grp in content.groups:
                return True

        logger.debug("Accès interdit à {}".format(content.url))
        return False

    def creer_contenu(self, path, parent=None):
        """
        Créer un contenu basique avec une url, un chemin et un éventuel parent
        :param path:
        :param parent:
        :return:
        """

        path = self._clean_path(path)
        url = self._get_url(path)

        content = BlogContent(url, path, parent=parent)
        return content

    def construire(self, path, parent=None):
        """
        Construit un contenu à partir d'un chemin
        :param path:
        :param parent:
        :return:
        """

        path = self._clean_path(path)
        main_file = os.path.join(path, self._category_file)

        content = self.creer_contenu(main_file, parent=parent)
        content.is_file = os.path.isfile(main_file)

        for item in os.scandir(path):

            # On met de côté les fichiers cachés
            if item.name.startswith('.'):
                continue

            child = None
            if item.is_dir():
                child = self.construire(item.path, parent=content)

            elif item.is_file():
                # On ignore les fichiers non markdown ou le fichier de catégorie
                if not item.name.endswith(self.markdown_extension) or item.name == self._category_file:
                    continue
                child = self.creer_contenu(item.path, parent=content)
                child.is_file = True

            if child:
                content.children.append(child)

        return content