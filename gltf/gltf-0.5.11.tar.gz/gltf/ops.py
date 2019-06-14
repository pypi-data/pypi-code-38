"""
The `ops` module contains a number of useful operations. These can be used to transform a loaded GLTF (in-place) in
various ways.

Use these like so:

```python
from gltf import GLTF
from gltf.ops import my_op

model = GLTF.load("input.glb")
my_op(model)  # These operate on the model in-place and return None
model.save("output.glb")
```
"""
import copy
import logging
from pprint import pprint

import numpy as np
from PIL import Image as PImage

from .buffers import Vec2Array, Vec3Array

logger = logging.getLogger(__name__)


def merge_animations(model):
    """
    Merges the animations of the model into the first animation. This is useful when you have a bunch of individual
    animations that should be played simultaneously in a GLTF viewer.
    """
    if not model.animations:
        return
    anim = model.animations[0]
    for an in model.animations[1:]:
        anim.channels.extend(an.channels)
    model.animations = [anim]


def sample_textures_to_materials(gltf, min_x=0.83, min_y=0.95):
    """
    Remove the UVs from a portion of the mapping, and recreate those as single-color materials. This is useful to
    remove texture coordinates from geometry that doesn't need it.
    """
    from .materials import Sampler
    images = dict()
    colors = dict()

    for n in (n for n in gltf.nodes if n.mesh):
        for p in n.mesh.primitives:
            if p.material is None or not p.texcoords:
                continue

            texcoord_idx = 0 if p.material.color_uv is None else p.material.color_uv
            texcoords = p.texcoords[texcoord_idx]
            indices = p.indices.data if p.indices else list(range(texcoords.count))

            tex = p.material.color_texture or p.material.diffuse_texture
            if tex is None:
                continue
            sampler = tex.sampler or Sampler()
            if id(tex) not in images:
                images[id(tex)] = PImage.open(tex.source.get_fp())
            img = images[id(tex)]

            color = None
            for i in indices:
                point = texcoords.data[i]
                if point[0] < min_x and point[1] < min_y:
                    break
                # Get the RGBA value for each point
                point = sampler.wrap_point(point)
                x = round((img.size[0] - 1) * point[0])
                y = round((img.size[1] - 1) * point[1])
                pixel = img.getpixel((x, y))
                if len(pixel) < 4:
                    pixel = list(pixel)
                    if len(pixel) == 1:
                        pixel *= 3
                    if len(pixel) == 3:
                        pixel.append(255)
                    else:
                        raise ValueError('Incorrect number of channels in pixel')

                pixel = tuple(pixel)
                if color is None:
                    color = pixel
                if pixel != color:
                    break
            else:
                # All texcoords mapped to the same color
                if color not in colors:
                    new_mat = copy.copy(p.material)
                    new_mat.base_color_factor = [(c/255) ** 2.2 for c in color]
                    if p.material.base_color_factor:
                        new_mat.base_color_factor[3] = p.material.base_color_factor[3]
                    new_mat.color_texture = None
                    new_mat.color_uv = None
                    new_mat.name = 'SampledTexture'
                    colors[color] = new_mat
                mat = colors[color]
                p.material = mat

                if texcoord_idx != 0 or len(p.texcoords) > 1:
                    p.texcoords = []
                    continue
                    raise NotImplementedError
                del p.texcoords[texcoord_idx]

    gltf.repair()


def round_accessors(model, decimal_places=3):
    for m in model.meshes:
        for p in m.primitives:
            p.positions.data = np.round(p.positions.data, decimal_places)
            if p.normals:
                p.normals.data = np.round(p.normals.data, decimal_places)
            if p.texcoords:
                for tc in p.texcoords:
                    tc.data = np.round(tc.data, decimal_places)


def reindex_all_primitives(model):
    for m in model.meshes:
        for p in m.primitives:
            if p.indices:
                reindex_primitive(p)


def reindex_primitive(p):
    if not p.indices:
        p.indices = list(range(p.positions.count))

    all_nums = set(list(range(p.positions.count)))
    used_nums = set([int(x) for x in p.indices.data])

    print(len(all_nums - used_nums) / int(p.positions.count))

    new_indices = []
    pos_norm_uv_map = {}
    new_positions = []
    new_normals = []
    new_uv = []

    for index in p.indices.data:
        pos = tuple([float(x) for x in p.positions.data[index]])
        norm = tuple([float(x) for x in p.normals.data[index]])
        # TODO: handle multiple texcoord sets
        uv = (
            None if not p.texcoords else
            tuple([float(x) for x in p.texcoords[0].data[index]])
        )
        pos_norm_uv = (pos, norm, uv)

        if pos_norm_uv not in pos_norm_uv_map:
            new_idx = len(new_positions)
            new_positions.append(pos)
            new_normals.append(norm)
            new_uv.append(uv)
            pos_norm_uv_map[pos_norm_uv] = new_idx

        new_indices.append(pos_norm_uv_map[pos_norm_uv])

    p.indices = new_indices
    p.normals = new_normals
    p.positions = new_positions
    if p.texcoords:
        p.texcoords[0] = Vec2Array(new_uv)


def merge_all_accessors(model):
    round_accessors(model)

    pos_norm_uv_map = {}
    pos_norm_map = {}
    positions = []
    position_acc = Vec3Array(positions)
    normals = []
    normal_acc = Vec3Array(normals)
    uvs = []
    uv_acc = Vec2Array(uvs)

    prims_with_uvs = []
    prims_without_uvs = []
    for m in model.meshes:
        for p in m.primitives:
            if not p.indices:
                p.indices = list(range(p.positions.count))
            if p.texcoords:
                prims_with_uvs.append(p)
            else:
                prims_without_uvs.append(p)

    prims_with_uvs.sort(key=lambda p: p.positions.count)
    prims_without_uvs.sort(key=lambda p: p.positions.count)

    # do prims with uvs first
    for p in prims_with_uvs + prims_without_uvs:
        new_indices = []

        for index in p.indices.data:
            pos = tuple([float(x) for x in p.positions.data[index]])
            norm = tuple([float(x) for x in p.normals.data[index]])
            pos_norm = (pos, norm)

            if p.texcoords:
                # TODO: Handle multiple texcoord sets
                uv = tuple([float(x) for x in p.texcoords[0].data[index]])
                pos_norm_uv = (pos, norm, uv)
                if pos_norm_uv in pos_norm_uv_map:
                    new_idx = pos_norm_uv_map[pos_norm_uv]
                else:
                    new_idx = len(positions)
                    pos_norm_uv_map[pos_norm_uv] = new_idx
                    positions.append(pos)
                    normals.append(norm)
                    uvs.append(uv)
                    if pos_norm not in pos_norm_map:
                        pos_norm_map[pos_norm] = new_idx
            elif pos_norm in pos_norm_map:
                new_idx = pos_norm_map[pos_norm]
            else:
                new_idx = len(positions)
                pos_norm_map[pos_norm] = new_idx
                positions.append(pos)
                normals.append(norm)

            new_indices.append(new_idx)
        p.indices = new_indices
        p.positions = position_acc
        p.normals = normal_acc
        if p.texcoords:
            p.texcoords[0] = uv_acc

    position_acc.data = positions
    normal_acc.data = normals
    uv_acc.data = uvs


def print_analysis(model):
    """
    Prints a filesize analysis of the GLTF file.
    """
    _accessor_cache = set()

    def _size(accessor):
        if id(accessor) in _accessor_cache:
            return 0
        else:
            _accessor_cache.add(id(accessor))

        n = accessor.data
        return n.size * n.itemsize

    def _primitive_extractor(path, prim, sizes):
        accessor = getattr(prim, path)
        if accessor is None:
            return

        if isinstance(accessor, list):
            many = accessor
            for accessor in many:
                sizes[path] += _size(accessor)
        else:
            sizes[path] += _size(accessor)

    def _format_bytes(byte_count):
        # 2**10 = 1024
        power = 2 ** 10
        n = 0
        powers = {0: '', 1: 'k', 2: 'M', 3: 'G', 4: 'T'}
        while byte_count > power:
            byte_count /= power
            n += 1
        return str(round(byte_count, 1)) + ' ' + str(powers[n]) + 'B'

    sizes = {
        "positions": 0,
        "normals": 0,
        "tangents": 0,
        "texcoords": 0,
        "indices": 0,
        "animation_translation": 0,
        "animation_rotation": 0,
        "animation_scale": 0,
        "animation_timesamples": 0,
    }

    for mesh in model.meshes:
        for prim in mesh.primitives:
            _primitive_extractor("positions", prim, sizes)
            _primitive_extractor("normals", prim, sizes)
            _primitive_extractor("tangents", prim, sizes)
            _primitive_extractor("texcoords", prim, sizes)
            _primitive_extractor("indices", prim, sizes)

    for anim in model.animations:
        for channel in anim.channels:
            sizes["animation_" + channel.target_path] += _size(channel.sampler.output)
            sizes["animation_timesamples"] += _size(channel.sampler.input)

    # TODO: JSON data

    # TODO: Textures

    pprint({k: _format_bytes(sizes[k]) for k in sizes})


def merge_redundant_meshes(model):
    """
    Merges meshes that have identical accessors and materials.
    """
    for i, m1 in enumerate(model.meshes):
        for j, m2 in enumerate(model.meshes[i:]):
            if m1 is not m2 and m1 == m2:
                for n in model.nodes:
                    if n.mesh is m2:
                        n.mesh = m1
    model.repair()


def repair(model, trim_to_scene=None):
    """
    Fixes various issues with GLTF files, doing the following tasks:

     - Remove empty nodes
     - Fix non-unit normals
     - Fix animation timesamples
     - Fix rotations on animations in cases where they render in a non-optimal path
     - Remove duplicate textures
     - Fix material values that are out of bounds
     - Index all primitives

    It's recommended that you always repair the file before you save it.

    The optional `trim_to_scene` parameter will strip all but the specified scene. By default it will do this for
    the root scene (identified by `gltf.scene`).
    """
    if trim_to_scene is None:
        trim_to_scene = model.scene is not None

    countable_attrs = ['scenes', 'nodes', 'meshes', 'accessors', 'cameras',
                       'materials', 'textures', 'images', 'samplers']
    counts = {
        attr: len(getattr(model, attr)) for attr in countable_attrs
    }

    # remove any nodes (from both the gltf and the scenes) that don't have a mesh/cam/children
    def recurse_nodes(node, valid_nodes=None):
        valid_children = []
        for cn in node.children:
            if recurse_nodes(cn, valid_nodes):
                valid_children.append(cn)
        node.children = valid_children

        is_valid = node.mesh or node.camera or node.children
        if not is_valid:
            # Check animation channel targets
            for anim in model.animations:
                for channel in anim.channels:
                    if channel.target_node == node:
                        is_valid = True
                        break
                else:
                    continue
                break
            else:
                # Check skin joints and skeleton
                for skin in model.skins:
                    if node == skin.skeleton or node in skin.joints:
                        is_valid = True
                        break

        if is_valid:
            if valid_nodes is not None and node not in valid_nodes:
                valid_nodes.append(node)
            return True

    for scene in model.scenes:
        valid_scene_nodes = []
        for n in scene.nodes:
            if recurse_nodes(n):
                valid_scene_nodes.append(n)
        scene.nodes = valid_scene_nodes

    if trim_to_scene:
        # remove all but the root scene, and keep only nodes descended from that scene
        if not model.scene:
            raise ValueError('Cannot trim to scene if there is no scene!')
        model.scenes = [model.scene]
        model.nodes = []
        for n in model.scene.nodes:
            recurse_nodes(n, model.nodes)
    else:
        nodes = model.nodes
        model.nodes = []
        for n in nodes:
            recurse_nodes(n, model.nodes)

    # remove duplicate meshes and cameras and skins
    meshes = model.remove_duplicates(model.meshes)
    model.meshes = []
    cameras = model.remove_duplicates(model.cameras)
    model.cameras = []
    skins = model.remove_duplicates(model.skins)
    model.skins = []

    # populate the used meshes, cameras, and skins
    for mesh in meshes:
        for node in model.nodes:
            if node.mesh == mesh and mesh not in model.meshes:
                model.meshes.append(mesh)
                break
    for camera in cameras:
        for node in model.nodes:
            if node.camera == camera and camera not in model.cameras:
                model.cameras.append(camera)
                break
    for skin in skins:
        for node in model.nodes:
            if node.skin == skin and skin not in model.skins:
                model.skins.append(skin)
                break

    for mat in model.materials:
        mat.repair()

    # get rid of duplicate materials and accessors
    materials = model.remove_duplicates(model.materials)
    model.materials = []
    accessors = model.remove_duplicates(model.accessors)
    model.accessors = []

    # go through all meshes and prims and find what materials and accessors are actually used
    # also index the primitive if it doesn't already have indices
    for mesh in model.meshes:
        for primitive in mesh.primitives:
            primitive.sort_joints()

            if not primitive.indices:
                reindex_primitive(primitive)

            # get all used materials
            for material in materials:
                if primitive.material == material and material not in model.materials:
                    model.materials.append(material)
                    break

            # get all used accessors
            for accessor in accessors:
                if accessor in primitive and accessor not in model.accessors:
                    model.accessors.append(accessor)
                    # don't break here, there can be multiple accessors in a prim

    # repair meshes
    for mesh in model.meshes:
        mesh.repair()

    # repair animations:
    model.animations = model.remove_duplicates(model.animations)
    for anim in model.animations:
        anim.repair()

    # add accessors used by animations
    for animation in model.animations:
        for sampler in animation.samplers:
            if sampler.input and sampler.input not in model.accessors:
                model.accessors.append(sampler.input)
            if sampler.output and sampler.output not in model.accessors:
                model.accessors.append(sampler.output)

    # add inverseBindMatrices accessors
    for skin in model.skins:
        if skin.inverse_bind_matrices and skin.inverse_bind_matrices not in model.accessors:
            model.accessors.append(skin.inverse_bind_matrices)

    # remove dupe textures
    textures = model.remove_duplicates(model.textures)
    model.textures = []

    # find which textures are used
    for texture in textures:
        for material in model.materials:
            if texture in material and texture not in model.textures:
                model.textures.append(texture)
                break

    # remove dupe images and samplers
    images = model.remove_duplicates(model.images)
    model.images = []
    samplers = model.remove_duplicates(model.samplers)
    model.samplers = []

    # find which images and samplers are used
    for texture in model.textures:
        for image in images:
            if texture.source == image and image not in model.images:
                model.images.append(image)
                break

        for sampler in samplers:
            if texture.sampler == sampler and sampler not in model.samplers:
                model.samplers.append(sampler)
                break

    for attr, count in counts.items():
        diff = len(getattr(model, attr)) - count
        if not diff:
            continue
        logger.info('{} {} {}'.format('Added' if diff > 0 else 'Removed',
                                      str(abs(diff)),
                                      attr))


def center(model):
    """
    Centers the model so that it rests on the origin. This is useful for preparing a model for use in AR.
    """

    bb = {
        'min_x': float('inf'),
        'min_y': float('inf'),
        'min_z': float('inf'),
        'max_x': float('-inf'),
        'max_z': float('-inf'),
    }

    if model.scene:
        nodes = model.scene.nodes
    else:
        nodes = model.get_root_nodes()

    def find_bounding_box(node, bb, parent_transform=None):
        transform, _ = node.get_transform(parent_transform)

        if node.mesh:
            for p in node.mesh.primitives:
                p_bb = np.array([
                    p.positions.min,
                    p.positions.max
                ], 'float32')
                p_bb = np.append(p_bb, np.ones([2, 1]), 1)
                p_bb = p_bb.dot(transform)[:, :3].astype('float32')

                min_x, min_y, min_z = np.nanmin(p_bb, axis=0).tolist()
                if min_x < bb['min_x']:
                    bb['min_x'] = min_x
                if min_z < bb['min_z']:
                    bb['min_z'] = min_z
                if min_y < bb['min_y']:
                    bb['min_y'] = min_y

                max_x, _, max_z = np.nanmax(p_bb, axis=0).tolist()
                if max_x > bb['max_x']:
                    bb['max_x'] = max_x
                if max_z > bb['max_z']:
                    bb['max_z'] = max_z

        for child in node.children:
            find_bounding_box(child, bb, transform)

    for n in (n for n in nodes if n.descendancy_has_mesh):
        find_bounding_box(n, bb, np.identity(4))

    translation = [-(bb['min_x'] + (bb['max_x'] - bb['min_x']) / 2),
                   -bb['min_y'],
                   -(bb['min_z'] + (bb['max_z'] - bb['min_z']) / 2)]

    transformation = np.identity(4)
    transformation[3, :3] += translation
    if not np.allclose(transformation, np.identity(4)):
        logger.info('Centering model using translation: '
                    '' + ', '.join(map(str, translation)))
        model.add_root_transform(transformation)
