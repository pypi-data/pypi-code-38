from pathlib import Path, PosixPath
from pygraphviz import AGraph

YFM_KEY = 'yfm'
ID_KEY = 'id'
NAME_KEY = 'name'
SECTIONS_KEY = 'sections'
TITLE_KEY = 'title'
REL_KEY = 'relates'
REL_TYPE_KEY = 'type'
REL_ID_KEY = 'rel_id'
REL_PATH_KEY = 'rel_path'
GV_KEY = 'gv_attributes'


class DublicateSectionID(Exception):
    pass


class Section:
    """Class which holds information about one chapter"""

    def __init__(self, name: str, ch_name: str, section_dict: dict):
        self.name = name
        self.chapter_name = ch_name
        self.title = section_dict[TITLE_KEY]
        self.yfm = section_dict[YFM_KEY]
        self.id = self.yfm.get(ID_KEY)
        self.gv = self.yfm.get(GV_KEY, {})
        self.type = self.yfm.get('type', '')

    def get_relations(self) -> list:
        """get list of relations as stated in yfm"""

        return self.yfm.get(REL_KEY, [])

    @property
    def full_name(self):
        return f'{self.chapter_name}_{self.name}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name} [{self.chapter_name}]>'


class Chapter:
    """Class which holds information about one chapter"""

    def __init__(self, chapter_dict: dict):
        self.name = chapter_dict[NAME_KEY]
        self._sections = []
        for sec_name, sec_dict in chapter_dict[SECTIONS_KEY].items():
            self.sections.append(Section(sec_name, self.name, sec_dict))

    @property
    def sections(self):
        return self._sections

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'


class MissingSection(Section):
    """
    Fake section which was related but wasn't found in meta section
    list. It has predefined styling of gray dashed node.
    """

    def __init__(self, name: str):
        self.name = name
        self.chapter_name = name
        self.title = name
        self.yfm = {}
        self.id = None
        self.gv = {'color': '#cccccc', 'style': 'dashed'}
        self.type = 'missing'


class Relation:
    """Class which holds information about one relation between two chapters"""

    def __init__(self,
                 parent: Chapter,
                 child: Chapter,
                 rel_dict: dict):
        self.parent = parent
        self.child = child
        self.type = rel_dict.get(REL_TYPE_KEY, '')
        self.gv = rel_dict.get(GV_KEY, {})

    def __repr__(self):
        return f'<Relation: {self.parent} -> {self.child}>'


def wrap_title(title: str, limit: int = 13, line_break: str = '\n'):
    """
    If title is longer than limit, attempt to wrap the long title into
    several lines using the line_break."""

    result = []
    if len(title) <= limit:
        return title
    part = ''
    for chunk in title.split(' '):
        part += ' ' + chunk
        if len(part) >= limit:
            result.append(part)
            part = ''
    if part:
        result.append(part)
    return line_break.join(result)


class ChaptersGraph:
    """Class which builds, holds and draws a chapters graph"""

    def __init__(self, chapter_list: list, src_path: PosixPath, config: dict = {}):
        # Flat list of Section objects
        self._sections = []
        # Mapping of chapter_name: Main section of chapter
        self._main_sections = {}
        # Mapping of section_id: Section object
        self._sections_with_id = {}
        for c in chapter_list:
            chapter = Chapter(c)
            self._main_sections[chapter.name] = chapter.sections[0]
            for s in chapter.sections:
                self._sections.append(s)
                if s.id:
                    if s.id in self._sections_with_id:
                        raise DublicateSectionID()
                    self._sections_with_id[s.id] = s
        self._src_path = src_path
        self._create_relations()
        self.config = config

    @property
    def relations(self):
        """List of Relation objects"""

        return self._relations

    @property
    def sections(self):
        """Flat list of Chapter objects"""

        return self._sections

    def __repr__(self):
        return f'<ChaptersGraph: {", ".join(str(c) for c in self.sections)}>'

    def _create_relations(self):
        """
        Fill up self._relations list.

        Relations can be of two types (and their combinations).
        Detailed syntax:

        relates:
            - rel_id: doc_id
              rel_type: link
            - rel_path: ../index.md

        Or short syntax:

        relates:
            - file2.md
            - doc_id
            - !project_path src/main.md
        """

        def get_name_from_path(rel_path: str or PosixPath):
            """
            Get proper relation name from rel_path.

            rel_path may be either path to related chapter relative to current
            chapter, or absolute path to the related chapter.

            Relation name must be a path relative to src dir.
            """

            if Path(self._src_path) in Path(rel_path).parents:  # absolute path
                result = Path(rel_path).relative_to(self._src_path)
            else:  # relative path
                result = Path(section.chapter_name).parent / rel_path
            return str(result)

        self._relations = []
        for section in self._sections:
            for rel_item in section.get_relations():
                parent = None
                if isinstance(rel_item, str):  # short syntax
                    rel_dict = {}
                    if rel_item in self._sections_with_id:
                        parent = self._sections_with_id[rel_item]
                    else:
                        parent_name = get_name_from_path(rel_item)
                        parent = self._main_sections.get(parent_name, MissingSection(parent_name))
                elif isinstance(rel_item, dict):  # detailed syntax
                    rel_dict = rel_item
                    if REL_ID_KEY in rel_item:
                        parent = self._sections_with_id.get(rel_item[REL_ID_KEY], MissingSection(rel_item[REL_ID_KEY]))
                    elif REL_PATH_KEY in rel_item:
                        parent_name = get_name_from_path(rel_item[REL_PATH_KEY])
                        parent = self._main_sections.get(parent_name, MissingSection(parent_name))

                if parent:
                    if isinstance(parent, MissingSection):
                        self._sections.append(parent)
                    self._relations.append(Relation(parent, section, rel_dict))

    def draw(self):
        """Draw graph with graphviz and save it to self.config['filename']"""

        default_gv_attributes = {
            'node': {'shape': 'rect', 'fontname': 'PT Sans'},
            'edge': {'arrowhead': 'open', 'arrowtail': 'open', 'fontname': 'PT Sans'},
            'graph': {'fontname': 'PT Sans'}
        }

        directed = self.config.get('directed', False)
        attrs = self.config.get('gv_attributes', default_gv_attributes)
        g = AGraph(directed=directed, strict=False)
        for k, v in attrs.get('graph', {}).items():
            g.graph_attr[k] = v
        for k, v in attrs.get('node', {}).items():
            g.node_attr[k] = v
        for k, v in attrs.get('edge', {}).items():
            g.edge_attr[k] = v
        for section in self.sections:
            if section.type and section.type in attrs:
                section_attrs = {**attrs[section.type], **section.gv}
            else:
                section_attrs = section.gv

            title = wrap_title(section.title)
            g.add_node(section.full_name, label=title, **section_attrs)
        for rel in self.relations:
            if rel.type and rel.type in attrs:
                rel_attrs = {**attrs[rel.type], **rel.gv}
            else:
                rel_attrs = rel.gv
            g.add_edge(rel.parent.full_name,
                       rel.child.full_name,
                       label=rel.type,
                       **rel_attrs)
        g.layout(prog='dot')
        output = self.config.get('filename', 'project_graph.png')
        g.draw(output)
