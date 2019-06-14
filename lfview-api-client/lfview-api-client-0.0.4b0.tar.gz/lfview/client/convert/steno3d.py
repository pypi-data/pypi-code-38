"""Function for converting Steno3D projects to Views"""
from __future__ import absolute_import

from lfview.resources import files, manifests, spatial
import numpy as np
import steno3d


def steno3d_to_view(steno3d_project, _lookup_dict=None):
    """Translate a Steno3D project into a View

    Input:
    **steno3d_project** - Instance of a Steno3D project; see
    :class:`steno3d.project.Project`
    """
    if not isinstance(steno3d_project, steno3d.Project):
        raise ValueError('Input must be steno3d Project')
    steno3d_project.validate()
    view = manifests.View(
        name=steno3d_project.title or '',
        description=steno3d_project.description or '',
        contents=[],
        elements=[],
    )
    if _lookup_dict is not None and hasattr(steno3d_project, '_upload_data'):
        _lookup_dict.update({steno3d_project._upload_data['uid']: view})
    for resource in steno3d_project.resources:
        if resource.__class__ not in translations:
            raise ValueError(
                'Unsupported resource type: {}'.format(
                    resource.__class__.__name__,
                )
            )
        translations[resource.__class__](
            resource, view, _lookup_dict=_lookup_dict
        )
    return view


def translate_binder(steno3d_binder, view, _lookup_dict=None):
    """Translate Steno3D binder into Data object"""
    if steno3d_binder.data.order != 'c':
        raise ValueError('Data ordering must be "c"')
    data = translations[steno3d_binder.data.__class__](
        steno3d_data=steno3d_binder.data,
        location=steno3d_binder.location,
        view=view,
        _lookup_dict=_lookup_dict,
    )
    return data


def translate_data_array(steno3d_data, location, view, _lookup_dict=None):
    """Translate Steno3D array data into Data, Mapping, and Arrays"""
    arr = files.Array(steno3d_data.array)
    data = spatial.DataBasic(
        name=steno3d_data.title or '',
        description=steno3d_data.description or '',
        array=arr,
        location=location,
    )
    if steno3d_data.colormap is not None:
        gradient = files.Array(steno3d_data.colormap)
        mapping = spatial.MappingContinuous(
            gradient=gradient,
            data_controls=[
                np.nanmin(steno3d_data.array),
                np.nanmax(steno3d_data.array),
            ],
            gradient_controls=[0., 1.],
            visibility=[True, True, True],
        )
        data.mappings = [mapping]
        view.contents += [mapping, gradient]
    view.contents += [arr, data]
    if _lookup_dict is not None and hasattr(steno3d_data, '_upload_data'):
        _lookup_dict.update({steno3d_data._upload_data['uid']: data})
    return data


def translate_data_category(steno3d_data, location, view, _lookup_dict=None):
    """Translate Steno3D category data into Data, Mappings, and Array"""
    arr = files.Array(steno3d_data.array)
    data = spatial.DataCategory(
        name=steno3d_data.title or '',
        description=steno3d_data.description or '',
        array=arr,
        location=location,
    )
    if steno3d_data.categories is not None:
        mapping = spatial.MappingCategory(
            values=steno3d_data.categories,
            indices=list(range(len(steno3d_data.categories))),
            visibility=[True] * len(steno3d_data.categories),
        )
        data.categories = mapping
        view.contents.append(mapping)
    if steno3d_data.colormap is not None:
        mapping = spatial.MappingCategory(
            values=steno3d_data.colormap,
            indices=list(range(len(steno3d_data.colormap))),
            visibility=[True] * len(steno3d_data.colormap),
        )
        if not data.categories:
            data.categories = mapping
        else:
            data.mappings = [mapping]
        view.contents.append(mapping)
    view.contents += [arr, data]
    if _lookup_dict is not None and hasattr(steno3d_data, '_upload_data'):
        _lookup_dict.update({steno3d_data._upload_data['uid']: data})
    return data


def translate_data_discrete(steno3d_data, location, view, _lookup_dict=None):
    """Translate Steno3D discrete data into Data, Mapping, and Array"""
    arr = files.Array(steno3d_data.array)
    if steno3d_data.range_visibility is not None:
        visibility = [bool(rv) for rv in steno3d_data.range_visibility]
    else:
        visibility = [True] * (len(steno3d_data.end_values) + 1)
    if steno3d_data.end_inclusive is not None:
        end_inclusive = [bool(ei) for ei in steno3d_data.end_inclusive]
    else:
        end_inclusive = [True] * len(steno3d_data.end_values)
    mapping = spatial.MappingDiscrete(
        end_points=steno3d_data.end_values,
        visibility=visibility,
        end_inclusive=end_inclusive,
        values=steno3d_data.colormap
        or [''] * (len(steno3d_data.end_values) + 1),
    )
    data = spatial.DataBasic(
        name=steno3d_data.title or '',
        description=steno3d_data.description or '',
        array=arr,
        location=location,
        mappings=[mapping]
    )
    view.contents += [arr, mapping, data]
    if _lookup_dict is not None and hasattr(steno3d_data, '_upload_data'):
        _lookup_dict.update({steno3d_data._upload_data['uid']: data})
    return data


def translate_texture(steno3d_tex, view, _lookup_dict=None):
    """Translate Steno3D texture into Texture and Image"""
    image = files.Image(steno3d_tex.image)
    tex = spatial.TextureProjection(
        name=steno3d_tex.title or '',
        description=steno3d_tex.description or '',
        image=image,
        origin=steno3d_tex.O,
        axis_u=steno3d_tex.U,
        axis_v=steno3d_tex.V,
    )
    view.contents += [image, tex]
    if _lookup_dict is not None and hasattr(steno3d_tex, '_upload_data'):
        _lookup_dict.update({steno3d_tex._upload_data['uid']: tex})
    return tex


def translate_point(steno3d_resource, view, _lookup_dict=None):
    """Translate Steno3D point into PointSet Element and Array"""
    vertices = files.Array(steno3d_resource.mesh.vertices)
    data = [
        translate_binder(dat, view, _lookup_dict=_lookup_dict)
        for dat in steno3d_resource.data
    ] + [
        translations[tex.__class__](tex, view, _lookup_dict=_lookup_dict)
        for tex in steno3d_resource.textures
    ]
    element = spatial.ElementPointSet(
        name=steno3d_resource.title or '',
        description=steno3d_resource.description or '',
        vertices=vertices,
        data=data,
    )
    if steno3d_resource.opts.color is not None:
        element.defaults.color.value = steno3d_resource.opts.color
    if steno3d_resource.opts.opacity is not None:
        element.defaults.opacity.value = steno3d_resource.opts.opacity
    view.contents += [vertices, element]
    view.elements += [element]
    if _lookup_dict is not None and hasattr(steno3d_resource, '_upload_data'):
        _lookup_dict.update({steno3d_resource._upload_data['uid']: element})
    return element


def translate_line(steno3d_resource, view, _lookup_dict=None):
    """Translate Steno3D line into LineSet Element and Arrays"""
    vertices = files.Array(steno3d_resource.mesh.vertices)
    segments = files.Array(steno3d_resource.mesh.segments)
    data = [
        translate_binder(dat, view, _lookup_dict=_lookup_dict)
        for dat in steno3d_resource.data
    ]
    element = spatial.ElementLineSet(
        name=steno3d_resource.title or '',
        description=steno3d_resource.description or '',
        vertices=vertices,
        segments=segments,
        data=data,
    )
    if steno3d_resource.mesh.opts.view_type == 'tube':
        opts = spatial.OptionsTubes(radius={'value': 10})
    else:
        opts = spatial.OptionsLines()
    opts.visible = True
    opts.color.value = 'random'
    opts.opacity.value = 1.
    if steno3d_resource.opts.color is not None:
        opts.color.value = steno3d_resource.opts.color
    if steno3d_resource.opts.opacity is not None:
        opts.opacity.value = steno3d_resource.opts.opacity
    element.defaults = opts
    view.contents += [vertices, segments, element]
    view.elements += [element]
    if _lookup_dict is not None and hasattr(steno3d_resource, '_upload_data'):
        _lookup_dict.update({steno3d_resource._upload_data['uid']: element})
    return element


def translate_surface(steno3d_resource, view, _lookup_dict=None):
    """Translate Steno3D surface into Surface Element and Arrays"""
    data = [
        translate_binder(dat, view, _lookup_dict=_lookup_dict)
        for dat in steno3d_resource.data
    ] + [
        translations[tex.__class__](tex, view, _lookup_dict=_lookup_dict)
        for tex in steno3d_resource.textures
    ]
    if isinstance(steno3d_resource.mesh, steno3d.Mesh2D):
        vertices = files.Array(steno3d_resource.mesh.vertices)
        triangles = files.Array(steno3d_resource.mesh.triangles)
        element = spatial.ElementSurface(
            name=steno3d_resource.title or '',
            description=steno3d_resource.description or '',
            vertices=vertices,
            triangles=triangles,
            data=data,
        )
        view.contents += [vertices, triangles]
    else:
        element = spatial.ElementSurfaceGrid(
            name=steno3d_resource.title or '',
            description=steno3d_resource.description or '',
            tensor_u=list(steno3d_resource.mesh.h1),
            tensor_v=list(steno3d_resource.mesh.h2),
            axis_u=steno3d_resource.mesh.U,
            axis_v=steno3d_resource.mesh.V,
            origin=steno3d_resource.mesh.O,
            data=data,
        )
        if (steno3d_resource.mesh.Z is not None
                and len(steno3d_resource.mesh.Z)):
            offset_w = files.Array(steno3d_resource.mesh.Z)
            element.offset_w = offset_w
            view.contents.append(offset_w)
    if steno3d_resource.opts.color is not None:
        element.defaults.color.value = steno3d_resource.opts.color
    if steno3d_resource.opts.opacity is not None:
        element.defaults.opacity.value = steno3d_resource.opts.opacity
    if steno3d_resource.mesh.opts.wireframe is not None:
        element.defaults.wireframe.active = steno3d_resource.mesh.opts.wireframe
    view.contents.append(element)
    view.elements += [element]
    if _lookup_dict is not None and hasattr(steno3d_resource, '_upload_data'):
        _lookup_dict.update({steno3d_resource._upload_data['uid']: element})
    return element


def translate_volume(steno3d_resource, view, _lookup_dict=None):
    """Translate Steno3D volume into Volume Element"""
    data = [
        translate_binder(dat, view, _lookup_dict)
        for dat in steno3d_resource.data
    ]
    element = spatial.ElementVolumeGrid(
        name=steno3d_resource.title or '',
        description=steno3d_resource.description or '',
        tensor_u=list(steno3d_resource.mesh.h1),
        tensor_v=list(steno3d_resource.mesh.h2),
        tensor_w=list(steno3d_resource.mesh.h3),
        axis_u=steno3d_resource.mesh.U,
        axis_v=steno3d_resource.mesh.V,
        axis_w=steno3d_resource.mesh.W,
        origin=steno3d_resource.mesh.O,
        data=data,
    )
    if steno3d_resource.opts.color is not None:
        element.defaults.color.value = steno3d_resource.opts.color
    if steno3d_resource.opts.opacity is not None:
        element.defaults.opacity.value = steno3d_resource.opts.opacity
    if steno3d_resource.mesh.opts.wireframe is not None:
        element.defaults.wireframe.active = steno3d_resource.mesh.opts.wireframe
    view.contents.append(element)
    view.elements += [element]
    if _lookup_dict is not None and hasattr(steno3d_resource, '_upload_data'):
        _lookup_dict.update({steno3d_resource._upload_data['uid']: element})
    return element


translations = {
    steno3d.DataArray: translate_data_array,
    steno3d.DataCategory: translate_data_category,
    steno3d.DataDiscrete: translate_data_discrete,
    steno3d.Texture2DImage: translate_texture,
    steno3d.Point: translate_point,
    steno3d.Line: translate_line,
    steno3d.Surface: translate_surface,
    steno3d.Volume: translate_volume,
}
