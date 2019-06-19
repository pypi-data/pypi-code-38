
class BlogFile:
    """
    Un fichier du système de blog : cela concerne uniquement
    les données qui ne représentent pas du contenu, c'est-à-dire
    des images, des documents, etc.
    """

    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.content = ""
        self.content_type = ""


class BlogContent:
    """
    Un contenu du système de blog : c'est une classe générique
    pour regrouper tout ce qui est commun aux objets manipulés
    """

    def __init__(self, url, path, is_file=False, parent=None):
        self.url = url
        self.path = path
        self.parent = parent
        self.is_file = is_file

        self.num = 0
        self.title = 'Sans titre'
        self.content = ''
        self.date = None
        self.icon = None
        self.groups = []

        self.children = []
        self.previous = None
        self.next = None
        self.is_loaded = False

    @property
    def depth(self):
        """
        :return: La profondeur du contenu
        """
        result = 0
        parent = self.parent
        while parent is not None:
            result += 1
            parent = parent.parent
        return result