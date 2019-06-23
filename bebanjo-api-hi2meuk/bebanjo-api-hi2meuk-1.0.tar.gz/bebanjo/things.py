import os
import math
import xml.etree.ElementTree as ET  # nosec (trused XML source)
import urllib.request
import re
import base64
import logging
from bebanjo import xml_utils
from bebanjo.error import XMLPassError, InvalidResourceError

DEFAULT_PER_PAGE = 50   # default number of items per page for pagination call

logger = logging.getLogger(__name__)

# pylint: disable=bare-except

# helper functions


def strip_url_params(url):
    m = re.match(r'([^?]*)\?', url)
    return m.group(1) if m else url


def image_dict_prepare(image_meta, name, url, fh):
    '''In-place update of image_meta. Sets encoding based on name_or_url. If fh provided, also
    prepares the the base64 encoded image file to send and related file metadata
    '''
    path = name or url
    try:
        m = re.search(r'[.](jp[e]?g|png)$', path, re.IGNORECASE)
        ext = m.group(1).lower()
        if ext in ['jpg', 'jpeg', 'png']:
            enc = 'jpeg'
        elif ext == 'png':
            enc = 'png'
        else:
            raise Exception
    except:
        raise ValueError('Unsupported image file name extension')
    else:
        if image_meta.get('encoding', None) is None:
            image_meta['encoding'] = enc
        if fh:
            mes = base64.b64encode(fh.read())
            attachment_str = f'data:image/{enc};base64,{str(mes, encoding="ascii")}'
            image_meta['attachment'] = attachment_str
            if image_meta.get('file_name', None) is None:
                image_meta['file_name'] = name


def overlay_url(left, right):
    '''Returns new url from left side overlayed with right side. left side must be full url
    '''
    split_left = left.split('/api')
    split_right = right.split('/api')
    if len(split_right) > 1:
        # right is full url
        return f'{split_left[0]}/api{split_right[1]}'
    # right is partial, make sure it has / prefix and append to left
    right = '/' + right if not right.startswith('/') else right
    return left + right


def name_from_resource(url):
    '''Returns resource name by finding the right most resource name from url
    '''
    return re.findall(r'([a-z_-]+)', url)[-1]


def send_body(url, method, data=b''):
    '''Makes a method call to Bebanjo with data (typically utf-8 encoded xml) and returns
    the response. Method should be put, post or delete depending on CRUD operation.
    '''
    logger.debug('%s to %s with payload: %s', method, url, data.decode())
    headers = {'Content-type': 'application/xml'}
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        http_response = urllib.request.urlopen(req)  # nosec
    except urllib.error.HTTPError as e:
        logger.error('%s %s returned status %s', method, url, e.code)
        raise
    else:
        logger.info('%s %s returned status %s', method, url, http_response.getcode())
        return http_response


class ThingFetcher():
    '''
    Methods for an API resource of unknown thing. Has capability to get from Bebanjo API
    and return a more distinctive class of what the resource is. Other methods also available
    but may not be appropriate for the resource. The app developer should is best place to
    know what methods are inappropriate for the resource.

    Note that te is not normally expected. It exists for compatibility with collection derrived
    class that does need it and to support asset generation when unit testing.
    '''
    def __init__(self, url=None, te=None):
        if url:                      # protect _url as may already be set through prior construction
            self._url = url
        self.members = {}    # basic collection capability. key is thing.id, value is thing
        if te:
            temp = self._objectify_te(te, url)
            self._copy_from(temp)

    @property
    def id(self):
        m_id = re.search(r'/(\d+)/?$', self._url)
        return int(m_id.group(1)) if m_id else None

    @property
    def url(self):
        "The self fetcher's URL if exists else empty string. Only settable via object construction"
        return self._url

    @property
    def summary_url(self):
        'The self getters URL in shortened form - without API path'
        m = re.match(r'.*/api/(.*)', self._url)
        return '//' + m.group(1) if m else self._url

    def get_member(self, _id):
        '''Returns member if exists else None
        '''
        return self.members.get(_id)

    def __getitem__(self, key):
        return self._meta1[key]  # pylint: disable=no-member

    def child_getters(self):
        '''Returns list of names of our child getters.
        '''
        r = []
        for k in dir(self):
            if not k.startswith('_'):
                v = getattr(self, k)
                if isinstance(v, ThingFetcher):
                    r.append(k)
        return r

    def __repr__(self):
        ri = []
        for k in '_meta1 metadata'.split():
            v = getattr(self, k, None)
            if v is not None:
                ri.append(f'{k}: {v.__repr__()}')
        return f'{self.__class__.__name__ }({", ".join(ri)})'

    def fetch(self, _id=None, *, name=None, external_id=None, expand=None):
        'Get a thing or things from Movida'
        opts = []
        res = ''
        if expand:
            _expand = expand if isinstance(expand, list) else [expand]
            opts.append('expand=' + ','.join(_expand))
        if _id:
            _id = str(_id)
            if not _id.isdigit():
                raise ValueError
            res += '/' + _id
        elif name:
            opts.append('name=' + str(name))
        elif external_id:
            opts.append('external_id=' + str(external_id))
        url = self._url + res
        opts = '?' + '&'.join(opts) if opts else ''
        r = self._get(url + opts)
        # if context of request was singular, return the item out of the collection
        if name or external_id:
            return list(r.members.values())[0] if r else None
        return r

    def _get(self, url):
        '''Do a GET call to Movida and transform the response into an instance of ThingFetcher
        compatible class.
        '''
        try:
            http_response = urllib.request.urlopen(url)  # nosec (url locked to http)
        except urllib.error.HTTPError as e:
            logger.error('GET %s returned status %s', url, e.code)
            raise
        else:
            logger.info('GET %s returned status %s', url, http_response.getcode())
            return self.objectify_response(http_response, url)

    def _generate_child_root_tag(self):
        '''Prepares an etree root element based on self
        '''
        root_tag = name_from_resource(self._url).replace('_', '-')
        if root_tag.endswith('s'):
            root_tag = root_tag[:-1]
        tag = ET.Element(root_tag)
        if root_tag == 'metadata':
            tag.set('type', 'document')
        return tag

    def create(self, meta=None, links=None):
        '''Attempts to create a new object in Movida/Sequence based on a given object
        '''
        root = self._generate_child_root_tag()
        xml = xml_utils.as_xml(root, meta, links)
        response = send_body(self._url, method='POST', data=xml)
        return self._add_member(self.objectify_response(response, self._url))

    def update(self, meta=None, links=None):
        '''Updating a thing's 1st class metadata and relations in Bebanjo, the response back
        updates our local/self. Exception raised if unsuccessful.
        '''
        root = ET.Element(self._snake_class_name())
        new = self._do_rest_xml_then_put(root, meta, links)
        self._copy_from(new)

    def _do_rest_xml_then_put(self, root, meta=None, links=None):
        xml = xml_utils.as_xml(root, meta, links)
        response = send_body(self._url, method='PUT', data=xml)
        return self.objectify_response(response, self._url)

    def delete(self, _id=None):
        '''Delete self or a child by ID or our metadata
        '''
        url = self._url
        if _id:
            # therefore a collection deleting a child, or singular deleting metadata
            if _id == 'metadata':
                setattr(self, 'metadata', Metadata(url=self.url + '/metadata'))
            else:
                if not str(_id).isdigit():
                    raise ValueError
                _ = self.members.pop(int(_id), None)  # pylint: disable=no-member
            url += f'/{_id}'
        else:
            # when deleting in self context it's not possible to remove us from parent; user to do
            pass
        send_body(url, method='DELETE')

    def objectify_response(self, http_response, url):
        '''Pass a http response and return an instance of ThingFetcher compatible class.
        '''
        body_b = http_response.read()
        logger.debug('response body: %s', body_b.decode())
        try:
            te = ET.fromstring(body_b)  # nosec (trused source)
        except ET.ParseError:
            raise XMLPassError({'msg': 'Bad response body XML', 'body': body_b.decode()})
        else:
            r = self._objectify_te(te, url=strip_url_params(url))
            return r

    def _objectify_te(self, te, url=None):
        '''Receives the tree element from get and has the task of determining what type of
        movida object it is and provides an instanciated object of correct type in return.
        '''
        links, meta1, meta2 = xml_utils.pass_te(te)
        url = links.pop('self', url)
        link_objects = {}
        for (k, v) in links.items():
            if k == 'metadata':
                link_objects[k] = Metadata(meta={}, url=v)
            else:
                link_objects[k] = ThingFetcher(v)
        if meta2:
            link_objects['metadata'] = Metadata(meta=meta2, url=url + '/metadata')
        root_tag = te.tag
        # If te is a Movida or Sequence API root node, return a replacement with links added
        if root_tag == 'movida':
            return type('MovidaAPI', (Collection,), link_objects)(url=self._url, te=te)
        new_class_name = root_tag.title().replace('_', '')
        # te (root) has attribute type="array" then it is a collection resource
        t = te.get('type')
        if t is not None and t == 'array':
            return type(new_class_name, (Collection,), {})(url=url, te=te)
        if new_class_name == 'Metadata':
            return Metadata(url=url, meta=meta1)
        return type(new_class_name, (ThingFetcher,),
                    {**link_objects, '_url': url, '_meta1': meta1})()

    def _snake_class_name(self):
        return type(self).__name__.lower().replace('_', '-')

    def create_image(self, fullpath, *, meta={}):
        '''Creates a new image instance in Movida based on fullpath and optional metadata (dict).
        Note: the parent collective object self may be a basic Fetcher class and not supporting
        child members. So we don't try to update members with the newly created image.
        '''
        if name_from_resource(self.url) != 'images':
            raise InvalidResourceError('create_image called on non-images resource')
        if fullpath.startswith('http'):
            meta['file-url'] = fullpath
            image_dict_prepare(meta, name=None, url=fullpath, fh=None)
            return self.create(meta)
        # else
        _, name = os.path.split(fullpath)
        with open(fullpath, 'rb') as fh:
            image_dict_prepare(meta, name=name, url=None, fh=fh)
        return self.create(meta)

    def add_platforms(self, targets):
        '''Creates target platforms. Expects an iterable of platform IDs or URLs. Returns self
        '''
        resource_name = name_from_resource(self.url)
        if resource_name != 'target_platforms':
            raise InvalidResourceError('add_platforms called on target_platforms resource')
        for pid in targets:
            platform_url = overlay_url(self.url, f'/api/platforms/{pid}')
            root = ET.Element('target-platforms')
            xml = xml_utils.as_xml(root, data={}, links={'platform': platform_url})
            send_body(self._url, method='POST', data=xml)
        return self

    def add_link(self, path, name=None):
        '''Adds a property to self of type fetcher so that it may be used to fetch from Movida.
        This feature avoids calls to Movida to get a predictable collection resource. Path can
        be relative to self or a full URL. Name of the property is based on last non-ID element
        of path or name if provided. Returns the new link's ThingFetcher object.
        '''
        path = overlay_url(self.url, path)
        name = name or name_from_resource(path)
        new_thing = Collection(url=path)
        setattr(self, name, new_thing)
        return new_thing

    def _add_member(self, child):
        '''Add an item to self.members and return item (basic collection capability).
        '''
        self.members[child.id] = child
        return child

    def _copy_from(self, other):
        for key in ['_meta1', 'metadata', 'members', 'next_page', 'per_page', 'items_available'] + \
            other.child_getters():
            val = getattr(other, key, None)
            if val:
                setattr(self, key, val)


class Metadata(ThingFetcher, dict):

    def __init__(self, *, url, meta={}):
        dict.__init__(self, meta)
        ThingFetcher.__init__(self, url)

    def __repr__(self):
        return f'{self.__class__.__name__}({dict.__repr__(self)})'

    def __str__(self):
        lines = (f'{k + ":":20} {v}' for k, v in self.members)
        return '\n'.join(lines)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def update(self, meta: dict):       # pylint: disable=arguments-differ
        root = ET.Element('metadata')
        root.set('type', 'document')
        new = self._do_rest_xml_then_put(root, meta)
        for k, v in new.items():
            self[k] = v


class Collection(ThingFetcher):

    def __init__(self, url=None, te=None):
        '''Called as a result of a get and te is supplied or add_link where te is not
        supplied and only the url of the link is known, implying a fetch call is required
        for the instance to be useful. The caller may set per-page post initialisation.
        '''
        def _set_page_data(e):
            # update next page and per page
            url = e.attrib.get('href')
            mg = re.search(r'[?&]per_page=([0-9]+)', url)
            self.per_page = int(mg.group(1)) if mg else None  # allow API response to override
            mg = re.search(r'[?&]page=([0-9]+)', url)
            return int(mg.group(1))

        ThingFetcher.__init__(self, url, te=None)
        self.next_page = None
        self.per_page = DEFAULT_PER_PAGE
        self.items_available = None
        self._item_cursor = 0
        if te is not None:
            for e in te.findall('*'):
                if e.tag == 'total-entries':
                    self.items_available = int(e.text)
                elif e.tag == 'link':
                    if e.attrib.get('rel') == 'next':
                        self.next_page = _set_page_data(e)
                    if e.attrib.get('rel') == 'prev':
                        _ = _set_page_data(e)   # not interested in prev page
                else:
                    o = self._objectify_te(e)
                    self.members[o.id] = o

    def get_paginated(self, page=1, per_page=DEFAULT_PER_PAGE):
        '''Get selected pages of referenced collection using pagination.  Hold only the last page
        of members locally, return self. Update page num, so any itteration continues from this
        point.
        '''
        opts = [f'page={page}', 'pagination=true']
        opts += [f'per_page={per_page}']
        opts = '?' + '&'.join(opts)
        new = self._get(self._url + opts)
        if new:
            self.per_page = per_page  # overwrites current, overwritten by returned value if exits
            self._copy_from(new)
            self.next_page = new.next_page  # auto-pagination - copy even when value tests false
            return self
        return None

    @property
    def count_pages(self):
        if isinstance(self.items_available, int) and self.per_page:
            return math.ceil(self.items_available / self.per_page)
        return None

    def __str__(self):
        return f'{type(self).__name__}  (url: {self._url}) Contains {len(self)} items.'

    def __len__(self):
        return len(self.members)

    # item itteration - requires indexable items like list but also need dict properties
    # so maitain list of keys alongside an ordered dict. Only require list when itterating.

    def _refresh_item_key_list(self):
        self._item_key_list = list(self.members.keys())  # pylint: disable=attribute-defined-outside-init

    def __getitem__(self, key):
        # Conveniently get a local member by ID e.g. title_groups[187341]
        return self.members[key]

    @property
    def keys(self):
        return self.members.keys

    # Itteration methods - actively calls get_paginated from remote

    def __iter__(self):
        self._item_cursor = 0
        self._refresh_item_key_list()
        return self

    def __next__(self):
        if self._item_cursor == len(self) and self.next_page:
            self._item_cursor = 0
            self.get_paginated(page=self.next_page, per_page=self.per_page)
            self._refresh_item_key_list()
        if self._item_cursor < len(self):
            item_key = self._item_key_list[self._item_cursor]
            item = self.members[item_key]
            self._item_cursor += 1
            return item
        raise StopIteration()
