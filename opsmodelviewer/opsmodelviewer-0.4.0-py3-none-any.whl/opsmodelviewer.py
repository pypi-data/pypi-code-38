import collections
import json
import warnings

import bokeh.models
import bokeh.palettes
import bokeh.plotting
import pandas as pd


class TagSpec():
    """Process structured integer tags into meaningful fields.

    TagSpec takes an iterable of field names, specified for each digit of a tag,
    and processes tags into named tuples. Tags that have fewer digits than the
    specifier are zero-filled to the specifier's length -- so the tag 104 is
    equivalent to the tag 00104 for a specifier that has five digits.

    Example 1
    ---------
    >>> tagspec = TagSpec(['kind', 'story', 'story', 'num', 'num'])
    >>> tagspec.process_tag(104)
    Tag(kind=0, story=1, num=4)
    >>> tagspec.process_tag(20912)
    Tag(kind=2, story=9, num=12)

    Example 2
    ---------
    >>> class TagKind(enum.Enum):
    ...     COLUMN = 0
    ...     BEAM = 1
    ...     BRACE = 2
    >>> tagspec = TagSpec(['kind', 'story', 'story', 'num', 'num'],
                          {'kind': TagKind})
    >>> tagspec.process_tag(104)
    Tag(kind=<TagKind.COLUMN: 0>, story=1, num=4)
    >>> tagspec.process_tag(20912)
    Tag(kind=<TagKind.BRACE: 2>, story=9, num=12)
    """

    def __init__(self, spec, mapping=None):
        """
        Parameters
        ----------
        spec : iterable
            Iterable of field names that define the meanings of each digit in
            processed tags.
        mapping : dict, optional
            Dict of callables that post-process the evaluated integers. Does not
            need to be defined for every field; if not present, the integer is
            returned unchanged for that field.
        """
        spec_dict = collections.defaultdict(lambda: [])
        for i, v in enumerate(spec):
            spec_dict[v].append(i)
        self.spec = spec
        self._specdict = dict(spec_dict)
        self._speclen = len(spec)
        self.mapping = {} if mapping is None else mapping
        self._tagfactory = collections.namedtuple('Tag', spec_dict.keys())

    def __repr__(self):
        return 'TagSpec(spec={!r}, mapping={!r})'.format(
            self.spec, self.mapping)

    def process_tag(self, tag):
        """Process a single tag.

        Parameters
        ----------
        tag : int
            Integer tag to process. Must have n or fewer digits, where n is the
            length of the specifier used to construct this object.

        Returns
        -------
        p : Tag
            Tag processed into descriptive fields.
        """
        tagstr = '{:0{l}d}'.format(tag, l=self._speclen)
        if len(tagstr) > self._speclen:
            raise ValueError('tag {} is longer than the spec'.format(tag))

        p = {field: [] for field in self._specdict.keys()}
        for field, indices in self._specdict.items():
            for i in indices:
                p[field].append(tagstr[i])
        for field, values in p.items():
            int_val = int(''.join(values))
            p[field] = self.mapping.get(field, lambda x: x)(int_val)

        return self._tagfactory(**p)

    def create_tag(self, default=0, **kwargs) -> int:
        """Create a tag from the spec.

        Parameters
        ----------
        default : int, optional
            Default value for fields. (default: 0)
        **kwargs
            Mapping of field names to values. Missing fields use `default`.

        Returns
        -------
        tag : int
            Tag that corresponds to the internal spec.

        Example
        -------
        >>> tagspec = TagSpec(['kind', 'story', 'num'])
        >>> tagspec.create_tag(kind=3, story=1, num=9)
        319
        >>> tagspec.create_tag(kind=1, num=8)
        108
        >>> tagspec.create_tag(kind=0, story=1, num=3)
        13
        """
        tag = [''] * self._speclen
        for field, indices in self._specdict.items():
            value = kwargs.get(field, default)
            field_length = len(indices)
            value_str = '{:0{}d}'.format(value, field_length)
            if len(value_str) > field_length:
                raise ValueError('{} exceeds the available'
                                 ' digits for field {!r}'.format(value, field))
            for i, d in zip(indices, value_str):
                tag[i] = d
        return int(''.join(tag))


class Node():
    def __init__(self, tag, x, y):
        self.tag = tag
        self.x = x
        self.y = y


class Element():
    def __init__(self, tag, inode, jnode):
        self.tag = tag
        self.inode = inode
        self.jnode = jnode


class Model():
    def __init__(self, spec, mapping=None, colorkey=None, palette=None):
        """
        Parameters
        ----------
        spec : iterable
            Iterable of field names that define the meanings of each digit in
            processed tags.
        mapping : dict, optional
            Dict of callables that post-process the evaluated integers. Does not
            need to be defined for every field; if not present, the integer is
            returned unchanged for that field.
        colorkey : str, optional
            Field name that provides keys for `palette`. Also used for legends.
        palette : list, optional
            List of colors to cycle through. (default: Category10_10)
        """
        if colorkey is not None and colorkey not in spec:
            raise ValueError('colorkey {!r} not found in spec {!r}'.format(
                colorkey, spec))
        if colorkey is not None and palette is None:
            palette = bokeh.palettes.Category10_10
        self.tagspec = TagSpec(spec, mapping=mapping)
        self.colorkey = colorkey
        self._colorkeyindex = self.tagspec._tagfactory._fields.index(colorkey)
        self.palette = palette
        self._palette_iter = iter(self.palette)
        self.nodes = {}
        self.elements = {}
        self._colormap = {}

    def __repr__(self):
        return '<Model {} {} nodes {} elements>'.format(
            self.tagspec, len(self.nodes), len(self.elements))

    def _get_next_color(self):
        """Return the next color in the palette, starting over when it ends."""
        try:
            return next(self._palette_iter)
        except StopIteration:
            self._palette_iter = iter(self.palette)
            return next(self._palette_iter)

    def _add_to_colormap(self, ptag):
        if self.colorkey is not None:
            colorval = ptag[self._colorkeyindex]
            if colorval not in self._colormap:
                self._colormap[colorval] = self._get_next_color()

    def add_node(self, tag, x, y):
        ptag = self.tagspec.process_tag(tag)
        self.nodes[tag] = Node(ptag, x, y)
        self._add_to_colormap(ptag)

    def add_element(self, tag, i, j):
        ptag = self.tagspec.process_tag(tag)
        self.elements[tag] = Element(ptag, i, j)
        self._add_to_colormap(ptag)

    def _node_data(self):
        tags = []
        x = []
        y = []
        color = []
        label = []
        meta = {key: [] for key in self.tagspec._specdict.keys()}
        for tag, node in self.nodes.items():
            tags.append(tag)
            x.append(node.x)
            y.append(node.y)
            if self.colorkey is not None:
                key = getattr(node.tag, self.colorkey)
                color.append(self._colormap[key])
                label.append(str(key))
            for key in meta.keys():
                meta[key].append(getattr(node.tag, key))
        if self.colorkey is None:
            color = None
            label = 'Nodes'
        data = pd.DataFrame({
            '_tag': tags,
            '_x': x,
            '_y': y,
            '_color': color,
            '_label': label,
            **meta
        }).set_index('_tag')
        metakeys = {key: '@' + key for key in meta.keys()}
        tooltips = {'node': '@_tag', 'x': '@_x', 'y': '@_y', **metakeys}
        return data, tooltips

    def _element_data(self):
        tags = []
        inodes = []
        jnodes = []
        x0 = []
        x1 = []
        y0 = []
        y1 = []
        color = []
        label = []
        meta = {key: [] for key in self.tagspec._specdict.keys()}
        for tag, element in self.elements.items():
            inode = self.nodes[element.inode]
            jnode = self.nodes[element.jnode]
            tags.append(tag)
            inodes.append(element.inode)
            jnodes.append(element.jnode)
            x0.append(inode.x)
            x1.append(jnode.x)
            y0.append(inode.y)
            y1.append(jnode.y)
            if self.colorkey is not None:
                key = getattr(element.tag, self.colorkey)
                color.append(self._colormap[key])
                label.append(str(key))
            for key in meta.keys():
                meta[key].append(getattr(element.tag, key))
        if self.colorkey is None:
            color = None
            label = 'Elements'
        data = pd.DataFrame({
            '_tag': tags,
            '_inode': inodes,
            '_jnode': jnodes,
            '_x0': x0,
            '_x1': x1,
            '_y0': y0,
            '_y1': y1,
            '_color': color,
            '_label': label,
            **meta
        }).set_index('_tag')
        metakeys = {key: '@' + key for key in meta.keys()}
        tooltips = {
            'element': '@_tag',
            'inode': '@_inode',
            'jnode': '@_jnode',
            **metakeys
        }
        return data, tooltips

    def show(self, output, title='Model'):
        bokeh.plotting.output_file(output)
        plot = bokeh.plotting.figure(title=title,
                                     toolbar_location='above',
                                     active_scroll='wheel_zoom')

        # Plot nodes
        node_data, node_tooltips = self._node_data()
        node_renderers = []
        for label, data in node_data.groupby('_label'):
            node_renderers.append(
                plot.circle(x='_x',
                            y='_y',
                            color='_color',
                            legend='_label',
                            size=8,
                            source=data))
        plot.add_tools(
            bokeh.models.HoverTool(renderers=node_renderers,
                                   tooltips=node_tooltips))

        # Plot elements
        element_data, element_tooltips = self._element_data()
        element_renderers = []
        for label, data in element_data.groupby('_label'):
            element_renderers.append(
                plot.segment(x0='_x0',
                             y0='_y0',
                             x1='_x1',
                             color='_color',
                             y1='_y1',
                             legend='_label',
                             line_width=2,
                             source=data))
        plot.add_tools(
            bokeh.models.HoverTool(line_policy='interp',
                                   renderers=element_renderers,
                                   tooltips=element_tooltips))

        plot.add_layout(plot.legend[0], 'right')
        plot.sizing_mode = 'scale_height'
        plot.legend.click_policy = 'hide'
        bokeh.plotting.show(plot)

    @classmethod
    def from_json(cls, file, spec, mapping=None, colorkey=None, palette=None, colormap=None):
        """Load a model from OpenSees JSON output.

        In OpenSees Tcl, create the output with::

            print -JSON {file}

        In OpenSeesPy, create the output with::

            ops.printModel('-JSON', '-file', file)

        Parameters
        ----------
        file : path-like
            Path to the JSON file.
        spec : iterable
            Iterable of field names that define the meanings of each digit in
            processed tags.
        mapping : dict, optional
            Dict of callables that post-process the evaluated integers. Does not
            need to be defined for every field; if not present, the integer is
            returned unchanged for that field.
        colorkey : str, optional
            Field name that provides keys for `palette`. Also used for legends.
        palette : list, optional
            List of colors to cycle through. (default: Category10_10)
        colormap : dict, optional
            Deprecated; use `palette` instead.
        """
        if colormap is not None:
            warnings.warn('colormap is deprecated; use palette instead',
                          category=DeprecationWarning)
            palette = list(colormap.values())
        model = cls(spec, mapping, colorkey, palette)

        with open(file) as f:
            d = json.load(f)
        nodes = d['StructuralAnalysisModel']['geometry']['nodes']
        elements = d['StructuralAnalysisModel']['geometry']['elements']
        for node in nodes:
            x, y = node['crd']
            model.add_node(node['name'], x, y)
        for element in elements:
            i, j = element['nodes']
            model.add_element(element['name'], i, j)

        return model


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='opsmodelviewer',
        description='Display an OpenSees model in an HTML plot.')
    parser.add_argument('source',
                        help='JSON file containing the model description.'
                        ' This file is produced by the OpenSees command'
                        ' `print -JSON {file}`.')
    parser.add_argument('-o',
                        '--output',
                        help='Output HTML file.',
                        default='model.html')
    parser.add_argument('--tagspec', help='Tag specifier.', nargs='*')
    parser.add_argument('--mapping',
                        help='Pairwise mapping of fields to functions.',
                        nargs='*')
    parser.add_argument('--colorkey', help='Tag field used to select colors.')
    parser.add_argument('--colormap',
                        help='Pairwise list of field names and RGB hex codes.',
                        nargs='*')
    parser.add_argument('--colormapfile',
                        help='JSON file containing color map definition.')
    args = parser.parse_args()

    def pairwise(iterable):
        "s -> (s0, s1), (s2, s3), (s4, s5) ..."
        a = iter(iterable)
        return zip(a, a)

    if args.mapping is not None:
        mapping = {field: eval(func) for field, func in pairwise(args.mapping)}
    else:
        mapping = None

    if args.colormapfile is None:
        if args.colorkey is not None:
            colormap = dict(pairwise(args.colormap))
        else:
            colormap = None
    else:
        with open(args.colormapfile) as f:
            colormap = json.load(f)

    model = Model.from_json(args.source, args.tagspec, mapping, args.colorkey,
                            colormap)
    model.show(args.output)


if __name__ == '__main__':
    main()
