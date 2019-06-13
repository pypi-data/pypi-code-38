r"""
:mod:`taika.ext.layouts` -- Jinja layouts
=========================================

This extension renders documents content trought a the Jinja2 templating engine. It also
renders the content of documents itself if any Jinja block/comment/var is detected.

Event
-----

This extension is subscribed to the :data:`site-post-read` event.

Payload
-------

When the content and the templates are rendered, certain payload is passed and becomes
accessible by both content and templates. This payload has two main keys: ``site`` and
``document``.

Using :code:`document` you can access the document attributes being processed, such as the
:code:`path`, :code:`content`, etc. Check :doc:`/reference/documents` for details.

Inside ``site``, the :class:`taika.Taika` is accessible.

.. note::

    Note that ``site.config`` returns a dictionary with all the sections included, so to access
    which extensions are listed you should use ``site.config.taika.extensions``. This is a long
    "import-like" statement, and probably we will shrink it in the future.

Frontmatter
-----------

.. data:: layout (str)

    The layout that should render the document. Should exist under the :data:`layouts_path`. If None
    the documents is not passed throught the template, but its body is still rendered.

Configuration
-------------

.. data:: layouts_path (dangling-list)

    Default: **./templates/**

    A list of paths from where the layouts will be loaded.

.. data:: layouts_options (dict)

    Default: **{}** (empty-dict)

    A dictionary (ini-style) of options to pass to the Jinja environment when created.

.. data:: layouts_default (str)

    Default: **index.html**

    The default layout if the document has no :code:`layout` defined.

.. data:: layouts_pattern (str)

    Default: *****

    Which files should be renderered. Default to all the files.

Default filters
---------------

Jinja

Process
-------

#. (pre-registering) The :class:`JinjaRenderer` is initialized with the configuration. The Jinja
   environment is created and the templates loaded.
#. Checks if the path of the document matches :data:`layouts_pattern`, if not, skips it.
#. Composes the layout using the document itself, so the document metadata is available directly.
#. If the content has any Jinja flag, it is renderered, so you can include Jinja syntax into the
   document text.
#. Then the content (rendered or not) is rendered throught the template :data:`layout`.
#. The document's content is modified.
#. Done!

Classes and Functions
---------------------
"""
import fnmatch
import logging
import platform
import sys
from pathlib import Path

try:
    import jinja2
except ImportError:
    print("This extension needs Jinja2, please install the jinja2 module.")
    sys.exit(1)

LAYOUTS_PATH = "./templates/"
LAYOUTS_DEFAULT = "index.html"
LAYOUTS_OPTIONS = {}
LAYOUTS_PATTERN = "*"

LOGGER = logging.getLogger(__name__)


class DocumentNotFound(Exception):
    pass


class JinjaRenderer(object):
    """This class holds the Jinja2 environment, removing the need to create it each time.

    Attributes
    ----------
    env : :class:`jinja2.Environment`
        The configured Jinja environment.
    layouts_pattern : str
        The pattern that the `path` attribute of documents should match in order to be processed.
    layouts_default : str
        The option so the :meth:`JinjaRenderer.render_content` can access it.
    """

    def __init__(self, config):
        layouts_path = config.get("layouts_path", LAYOUTS_PATH)
        layouts_options = config.get("layouts_options", LAYOUTS_OPTIONS)

        loader = jinja2.FileSystemLoader(layouts_path)
        self.env = jinja2.Environment(loader=loader, **layouts_options)

        self.layouts_default = config.get("layouts_default", LAYOUTS_DEFAULT)
        self.layouts_pattern = config.get("layouts_pattern", LAYOUTS_PATTERN)

    def render_content(self, site):
        payload = {}
        payload["site"] = site

        for document in site.documents:
            if not fnmatch.fnmatch(document["path"], self.layouts_pattern):
                continue

            payload["document"] = document
            content = document["content"]

            if self._has_block(content) or self._has_comment(content) or self._has_var(content):
                content = self.env.from_string(content).render(**payload)

            document["pre_render_content"] = payload["document"]["content"] = content

            template_name = document.get("layout", self.layouts_default)
            if template_name is not None:
                template = self.env.get_template(template_name)
                content = template.render(**payload)

            document["content"] = content

    def _has_block(self, s):
        return self.env.block_start_string in s and self.env.block_end_string in s

    def _has_var(self, s):
        return self.env.variable_start_string in s and self.env.variable_end_string in s

    def _has_comment(self, s):
        return self.env.comment_start_string in s and self.env.comment_end_string in s


@jinja2.contextfilter
def link(context, path):
    is_absolute = False

    path = Path(path)
    if platform.system() == "Windows":
        path = path.resolve()

    if path.is_absolute():
        path = Path(*path.parts[1:])
        is_absolute = True

    LOGGER.debug(
        f"Link ContextFilter --> From:'{context['document']['path']}' the document '{path}' is"
        "requested."
    )
    for doc in context["site"].documents:
        if doc["path"] == path:
            return_path = doc["url"]
            break
    else:
        raise DocumentNotFound(path)

    if is_absolute:
        return "/" + str(return_path)
    return return_path


def setup(site):
    renderer = JinjaRenderer(site.config)
    renderer.env.filters.update({"link": link})
    site.events.register("site-post-read", renderer.render_content)
