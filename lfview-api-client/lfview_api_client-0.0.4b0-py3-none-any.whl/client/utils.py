"""Utility functions to support session uploads and downloads"""
from __future__ import print_function

from collections import OrderedDict
from io import BytesIO
import re

from lfview.resources import files, manifests, scene, spatial
import numpy as np
import properties
import properties.extras
import requests
from six import string_types

from .constants import CHUNK_SIZE, IGNORED_PROPS, RESOURCE_REGISTRIES

try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    pass


def upload_chunk(url, dat, start, stop, total, content_type, session):
    """Upload a chunk of a file"""
    res = session.put(
        url=url,
        data=dat,
        headers={
            'Content-Length': str(stop - start),
            'Content-Type': content_type,
            'Content-Range': 'bytes {start}-{stop}/{total}'.format(
                start=start,
                stop=stop - 1,
                total=total,
            ),
        },
    )
    return res


def upload_array(arr, url, chunk_size=CHUNK_SIZE, session=None):
    """Upload an array to specified URL"""
    length = arr.nbytes
    arr_bytes = arr.tobytes()
    if not session:
        session = requests.Session()
    for start in range(0, length, chunk_size):
        stop = min(start + chunk_size, length)
        res = upload_chunk(
            url=url,
            dat=arr_bytes[start:stop],
            start=start,
            stop=stop,
            total=length,
            content_type='application/octet-stream',
            session=session,
        )
    return res


def upload_image(img, url, chunk_size=CHUNK_SIZE, session=None):
    """Upload an image to specified URL"""
    img.seek(0, 2)
    length = img.tell()
    if not session:
        session = requests.Session()
    for start in range(0, length, chunk_size):
        stop = min(start + chunk_size, length)
        img.seek(start)
        res = upload_chunk(
            url=url,
            dat=img.read(stop - start),
            start=start,
            stop=stop,
            total=length,
            content_type='image/png',
            session=session,
        )
    return res


def is_pointer(prop):
    """Return true if prop is a Pointer property or Union of Pointers"""
    if isinstance(prop, properties.extras.Pointer):
        return True
    if not isinstance(prop, properties.Union):
        return False
    return all(is_pointer(p) for p in prop.props)


def is_list_of_pointers(prop):
    """Return true if prop is a container property with Pointer values"""
    if not isinstance(prop, properties.Tuple):
        return False
    return is_pointer(prop.prop)


def find_class_from_resp(url, resp_type=None):
    """Return class that matches input URL and 'type' from JSON response"""
    if resp_type:
        if '/' in resp_type:
            return find_class_from_types(*resp_type.split('/'))
        return find_class_from_types(resp_type, None)
    return find_class_from_types(*types_from_url(url))


def find_class_from_types(base_type, sub_type):
    """Search resource registries class that matches specified type"""
    if base_type:
        for registry in RESOURCE_REGISTRIES:
            for value in registry.values():
                if (not value.__name__.startswith('_')
                        and getattr(value, 'BASE_TYPE', None) == base_type
                        and getattr(value, 'SUB_TYPE', None) == sub_type):
                    return value
    raise ValueError(
        'Unable to find class matching {}{}'.format(
            base_type, '/{}'.format(sub_type) if sub_type else ''
        )
    )


def types_from_url(url):
    """Extract API resource base-type and sub-type from URL

    Valid inputs include project service, view service and app URLs.
    """
    if match_url_slide(url):
        return 'slides', None
    if match_url_feedback(url):
        return 'feedback', None
    if match_url_app(url) or match_url_project(url) or match_url_view(url):
        return 'views', None
    resource_re = (
        r'^.+/api/v1/(view/[a-z0-9]+|project)/[a-z0-9]+/[a-z0-9]+'
        r'/(?P<basetype>[a-z]+)/(?P<subtype>[a-z]+)/[a-z0-9]+$'
    )
    match = re.search(resource_re, url)
    if match:
        groupdict = match.groupdict()
        return groupdict['basetype'], groupdict['subtype']
    raise ValueError('Unknown resource type from {}'.format(url))


def compute_children(resource):
    """Recursively traverse pointers to find all nested resources

    This function is used to identify all resources that need to be
    exposed on a View manifest contents list.
    """
    children = []
    for name, prop in sorted(resource._props.items()):
        value = getattr(resource, name)
        if name in IGNORED_PROPS or value is None:
            continue
        elif is_pointer(prop):
            if isinstance(value, files.base._BaseUIDModel):
                children += compute_children(value)
            children.append(value)
        elif is_list_of_pointers(prop):
            for val in value:
                if isinstance(val, files.base._BaseUIDModel):
                    children += compute_children(val)
                children.append(val)
    children = list(OrderedDict.fromkeys(children))
    return children


def touch(resource, recursive=False):
    """Indicate that a resource has been updated since last upload

    By default, when a property is changed, the resource is automatically
    touched. You may also specify :code:`recursive=True` to touch all
    child resources.
    """
    resource._touched = True
    if recursive:
        for item in compute_children(resource):
            if isinstance(item, string_types):
                continue
            item._touched = True


def process_uploaded_resource(resource, url, verbose=False, final=True):
    """Save url as attribute on resource and setup change observer"""
    if not getattr(resource, '_url', None):
        resource._url = url
    resource._future_url = None
    if not getattr(resource, '_change_observer', None):
        resource._change_observer = properties.observer(
            resource,
            names=properties.everything,
            func=lambda resource, _: touch(resource),
            change_only=True,
        )
    resource._touched = False
    if verbose:
        log('Finished upload of {}'.format(resource), final)
    return resource


def is_uploaded(resource):
    """Determine if resource is up-to-date with the server"""
    if isinstance(resource, string_types):
        return True
    if not getattr(resource, '_url', None):
        return False
    return not getattr(resource, '_touched', True)


def construct_upload_dict(resource):
    """Method to construct upload body from resource with pointers"""
    json_dict = {}
    for name, prop in resource._props.items():
        value = getattr(resource, name)
        if name in IGNORED_PROPS or value is None:
            continue
        if is_pointer(prop):
            json_value = getattr(value, '_url', value)
        elif is_list_of_pointers(prop):
            json_value = []
            for val in value:
                json_value.append(getattr(val, '_url', val))
        else:
            json_value = prop.serialize(value, include_class=False)
        json_dict.update({name: json_value})
    return json_dict


def build_resource_from_json(url, resource_json, copy):
    """Helper method to construct Python object from resource JSON"""
    resource_class = find_class_from_resp(
        url=url, resp_type=resource_json.get('type')
    )
    resource = resource_class.deserialize(
        properties.filter_props(resource_class, resource_json)[0]
    )
    # Patch in elements since they may not be present on API response
    if (isinstance(resource, manifests.View)
            and 'elements' not in resource_json):
        resource.elements = [
            item for item in resource.contents
            if item.split('/')[-3] == 'elements'
        ]
    if isinstance(resource, files.base._BaseFile):
        file_resp = resource_json['links']['location']
        if not file_resp.ok:
            raise ValueError(file_resp.text)
        data = file_resp.content
        if isinstance(resource, files.Array):
            resource.array = np.frombuffer(
                buffer=data,
                dtype=files.files.ARRAY_DTYPES[resource.dtype][0],
            ).reshape(resource.shape)
        elif isinstance(resource, files.Image):
            fid = BytesIO()
            fid.write(data)
            fid.seek(0)
            resource.image = fid
        else:
            raise ValueError(
                'Unknown file resource: {}'.format(
                    resource.__class__.__name__
                )
            )
    if not copy:
        process_uploaded_resource(resource, url, False)
    return resource


def populate_resource_pointers(resource, lookup_dict):
    """Helper method to update pointer URLs with corresponding objects"""
    for name, prop in sorted(resource._props.items()):
        value = getattr(resource, name)
        if value is None:
            continue
        elif is_pointer(prop):
            if value not in lookup_dict:
                new_value = value
            else:
                new_value = lookup_dict[value]
            setattr(resource, name, new_value)
        elif is_list_of_pointers(prop):
            new_value_list = []
            for val in value:
                if val not in lookup_dict:
                    new_value_list.append(val)
                else:
                    new_value_list.append(lookup_dict[val])
            setattr(resource, name, new_value_list)


def match_url_app(url):
    """Return re match object if input is an app URL

    These take the form:

    https://example.com/app/org123/proj456/view789
    """
    app_url_re = (
        r'^(?P<base>.+)/app'
        r'/(?P<org>[a-z0-9]+)/(?P<proj>[a-z0-9]+)'
        r'/(?P<view>[a-z0-9]+)$'
    )
    return re.search(app_url_re, url)


def match_url_project(url):
    """Return re match object if input is a Project-service View URL

    These take the form:

    https://example.com/api/v1/project/org123/proj456/views/view789
    """
    proj_url_re = (
        r'^(?P<base>.+)/api/v1/project'
        r'/(?P<org>[a-z0-9]+)/(?P<proj>[a-z0-9]+)'
        r'/views/(?P<view>[a-z0-9]+)$'
    )
    return re.search(proj_url_re, url)


def match_url_view(url):
    """Return re match object if input is a View-service View URL

    These take the form:

    https://example.com/api/v1/view/org123/proj456/view789
    """
    view_url_re = (
        r'^(?P<base>.+)/api/v1/view'
        r'/(?P<org>[a-z0-9]+)/(?P<proj>[a-z0-9]+)'
        r'/(?P<view>[a-z0-9]+)$'
    )
    return re.search(view_url_re, url)


def match_url_slide(url):
    """Return re match object if input is a View-service Slide URL

    These take the form:

    https://example.com/api/v1/view/org123/proj456/view789/slides/slide012
    """
    slide_url_re = (
        r'^.+/api/v1/view/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/slides/[a-z0-9]+$'
    )
    return re.search(slide_url_re, url)


def match_url_feedback(url):
    """Return re match object if input is a View-service Feedback URL

    These take the form:

    https://example.com/api/v1/view/org123/proj456/view789/slides/slide012/feedback/fb345
    """
    feedback_url_re = (
        r'^.+/api/v1/view/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/slides/[a-z0-9]+'
        r'/feedback/[a-z0-9]+$'
    )
    return re.search(feedback_url_re, url)


def convert_url_app_to_project(url):
    """Converts app URL to Project-service View URL

    Given input of:

    https://example.com/app/org123/proj456/view789

    this function returns:

    https://example.com/api/v1/project/org123/proj456/views/view789
    """
    match = match_url_app(url)
    if not match:
        raise ValueError('Invalid app url: {}'.format(url))
    proj_url_string = r'{base}/api/v1/project/{org}/{proj}/views/{view}'
    return proj_url_string.format(**match.groupdict())


def convert_url_project_to_view(url):
    """Converts Project-service View URL to View-service View URL

    Given input of:

    https://example.com/api/v1/project/org123/proj456/views/view789

    this function returns:

    https://example.com/api/v1/view/org123/proj456/view789
    """
    match = match_url_project(url)
    if not match:
        raise ValueError('Invalid project url: {}'.format(url))
    view_url_string = r'{base}/api/v1/view/{org}/{proj}/{view}'
    return view_url_string.format(**match.groupdict())


def drawing_plane_from_camera(camera):
    """Estimate a drawing plane perpendicular to camera

    This is used to calculate a default annotation plane for slides if
    none is provided. The output does not exactly recreate the annotation
    plane calculation in the web app; however, the estimate is close enough
    to work ok.
    """
    qi, qj, qk, qr = camera.rotation
    if all([rot == 0 for rot in camera.rotation]):
        s = 1
    else:
        s = 1 / (qi * qi + qj * qj + qk * qk + qr * qr)**0.5
    axis_length = camera.radius / camera.zoom
    input_axes = [[axis_length, 0., 0.], [0., axis_length, 0.]]
    axis_u, axis_v = [
        [
            (1 - 2 * s * (qj * qj + qk * qk)) * axis[0] +
            2 * s * (qi * qj - qk * qr) * axis[1] +
            2 * s * (qi * qk + qj * qr) * axis[2],
            2 * s * (qi * qj + qk * qr) * axis[0] +
            (1 - 2 * s * (qi * qi + qk * qk)) * axis[1] +
            2 * s * (qj * qk - qi * qr) * axis[2],
            2 * s * (qi * qk - qj * qr) * axis[0] +
            2 * s * (qj * qk + qi * qr) * axis[1] +
            (1 - 2 * s * (qi * qi + qj * qj)) * axis[2],
        ] for axis in input_axes
    ]
    origin = [
        camera.target[0] - axis_u[0] / 2 - axis_v[0] / 2,
        camera.target[1] - axis_u[1] / 2 - axis_v[1] / 2,
        camera.target[2] - axis_u[2] / 2 - axis_v[2] / 2,
    ]
    plane = scene.DrawingPlane(
        origin=origin,
        axis_u=axis_u,
        axis_v=axis_v,
    )
    return plane


def extra_slide_validation(slide, element_list):
    """Perform extra validation of a Slide object

    Slide loading in the web app has limitations beyond the built-in
    Slide object validation. This includes:
    - references to elements, data, and textures must be URLs
    - all elements must have a corresponding view in the slide
    """
    views = slide.scene.plots[0].views
    try:
        view_uids = set(view.element.split('/')[-1] for view in views)
    except AttributeError:
        raise properties.ValidationError(
            'Elements specified in plot views must be URL strings'
        )
    element_uids = set(elem.split('/')[-1] for elem in element_list)
    if view_uids != element_uids:
        raise properties.ValidationError(
            'All Elements in the View must be placed in the plot; '
            'to hide the Element set visible=False'
        )
    for view in views:
        for attr in 'color', 'opacity', 'radius':
            opts = getattr(view, attr, None)
            if not opts:
                continue
            if opts.data and not isinstance(opts.data, string_types):
                raise properties.ValidationError(
                    'Data specified in plot views must be URL strings'
                )
        if getattr(view, 'textures', None):
            for tex in view.textures:
                if not isinstance(tex.data, string_types):
                    raise properties.ValidationError(
                        'Texture data specified in plot views must be '
                        'URL strings'
                    )


def is_color_mapping(mapping):
    """Return True if mapping maps data into color values"""
    if isinstance(mapping, (spatial.MappingContinuous, string_types)):
        return True
    if not mapping.values:
        return False
    return isinstance(mapping.values[0], tuple)


def sanitize_data_colormaps(data):
    """Update data mappings to be well behaved with the web visualization

    For discrete and category data, web visualization expects
    the first mapping to be a color map. If this is not the case, it
    fails to load. This function re-orders the mappings or creates a
    stand-in mapping with random colors to meet this limitation.
    """
    if not data.mappings:
        data.mappings = []
        if not isinstance(data, spatial.DataCategory):
            return data
    elif is_color_mapping(data.mappings[0]):
        return data
    color_mapping_indices = [
        ind for ind, mapping in enumerate(data.mappings)
        if not isinstance(mapping, spatial.MappingContinuous)
        and is_color_mapping(mapping)
    ]
    if color_mapping_indices:
        index = color_mapping_indices[0]
        data.mappings = (
            [data.mappings[index]] + data.mappings[:index] +
            data.mappings[index + 1:]
        )
    elif hasattr(data, 'categories') and is_color_mapping(data.categories):
        data.mappings = [data.categories] + data.mappings
    else:
        new_mapping = properties.copy(data.mappings[0])
        new_mapping.values = ['random'] * len(new_mapping.values)
        data.mappings = [new_mapping] + data.mappings
    return data


def log(message, final=True, total_length=70):
    """Simple print logger that facilitates repeated messages on one line"""
    end_buffer = max(20, total_length - len(message))
    print(
        '\r{}'.format(message),
        end=end_buffer * ' ' + ('\n' if final else '\r'),
    )


class SynchronousExecutor:
    """Synchronous executor with similar API to ThreadPoolExecutor

    This class implements :code:`submit` and :code:`shutdown`.

    Note: Exceptions that occur during execution will be raised on
    :code:`submit`; this differs from ThreadPoolExecutor where
    exceptions are not raised until accessing the result.
    """

    @staticmethod
    def submit(func, *args, **kwargs):
        """Execute input function and store result in synchronous future"""
        return SynchronousFuture(func(*args, **kwargs))

    @staticmethod
    def shutdown(wait=True):
        """Shutting down a SynchronousExecutor does nothing"""
        pass


class SynchronousFuture:
    """Result of submitting a function to SynchronousExecutor

    Follows a similar API to concurrent.futures.Future. By the
    synchronous definition, these futures are "done" on creation.
    """

    def __init__(self, result):
        self._result = result

    def done(self):
        """Returns True since result is defined on instantiation"""
        return True

    def result(self):
        """Returns the result provided on instantiation"""
        return self._result


def get_default_executor(parallel, verbose, workers=None):
    """Return default parallel or synchronous executor"""
    if parallel:
        if verbose:
            log('Initializing thread pool', False)
        return ThreadPoolExecutor(max_workers=workers)
    return SynchronousExecutor()
