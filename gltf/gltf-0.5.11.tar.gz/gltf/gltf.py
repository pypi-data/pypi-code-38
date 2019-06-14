import json
import os
from io import BytesIO

import numpy as np

from . import ops
from .animations import Animation, Skin
from .buffers import (
    Buffer, BufferView, Vec4Array, Vec3Array, Vec2Array, ScalarArray, Mat4Array
)
from .nodes import Node, Camera, Mesh
from .materials import Material, Texture, Sampler, Image
from .utils import binary_to_uri


class Scene(object):
    name = None
    nodes = None

    def __init__(self, scene=None, gltf=None, nodes=None, name=None):
        if scene:
            self.name = scene.get('name')
            self.nodes = [gltf.nodes[i] for i in scene.get('nodes', [])]
        else:
            self.nodes = nodes or []
            self.name = name

    def __repr__(self):
        return self.name or super(Scene, self).__repr__()

    def render(self, gltf):
        scene = {}
        if self.name:
            scene['name'] = self.name
        if self.nodes:
            scene['nodes'] = [gltf.index_node(n) for n in self.nodes]
        return scene


class GLTF(object):
    MAGIC = 0x46546C67
    JSON_CHUNK = 0x4E4F534A
    BINARY_CHUNK = 0x004E4942
    scene = None
    ignore_http_uri = False

    def __init__(self, folder=None, filename=None, binary=False):
        self.scenes = []
        self.cameras = []
        self.meshes = []
        self.nodes = []
        self.materials = []
        self.textures = []
        self.samplers = []
        self.accessors = []
        self.images = []
        self.buffer_views = []
        self.buffers = []
        self.skins = []
        self.animations = []
        self.extensions_used = []
        self.folder = folder
        self.filename = filename
        self.asset = {
            'version': '2.0',
            'generator': 'Seek glTF Generator',
        }
        self.default_to_glb = binary

    def index(self, component, obj):
        if not hasattr(self, component):
            raise AttributeError(component)
        arr = getattr(self, component)
        if obj not in arr:
            arr.append(obj)
        return arr.index(obj)

    def index_node(self, node):
        for i, n in enumerate(self.nodes):
            if n is node:
                return i
        self.nodes.append(node)
        return len(self.nodes) - 1

    @staticmethod
    def simple_model(name, folder=None):
        gltf = GLTF(folder)
        gltf.scene = Scene()
        mesh = Mesh()
        gltf.meshes.append(mesh)
        node = Node(mesh=mesh, name=name)
        gltf.nodes.append(node)
        gltf.scene.nodes.append(node)

        return gltf, mesh

    @staticmethod
    def can_load(path_or_bytes, gltf=False, glb=False):
        if not gltf:
            first_8_bytes = b''
            if type(path_or_bytes) is str:
                if os.path.exists(path_or_bytes) and not os.path.isdir(path_or_bytes):
                    with open(path_or_bytes, 'rb') as f:
                        first_8_bytes = f.read(8)
            if type(path_or_bytes) is BytesIO:
                path_or_bytes.seek(0)
                first_8_bytes = path_or_bytes.read(8)
            if isinstance(path_or_bytes, (bytes, bytearray)):
                first_8_bytes = path_or_bytes[:8]

            if first_8_bytes:
                magic, glb_version = np.frombuffer(first_8_bytes, dtype='uint32')
                if magic == GLTF.MAGIC and glb_version == 2:
                    return 'glb'
        if not glb:
            data_dict = {}
            if type(path_or_bytes) is dict:
                data_dict = path_or_bytes
            try:
                if type(path_or_bytes) is str:
                    if os.path.exists(path_or_bytes) and not os.path.isdir(path_or_bytes):
                        with open(path_or_bytes, 'r') as f:
                            data_dict = json.load(f)
                    else:
                        data_dict = json.loads(path_or_bytes)
                if isinstance(path_or_bytes, (bytes, bytearray)):
                    data_dict = json.loads(path_or_bytes.decode())
                if type(path_or_bytes) is BytesIO:
                    path_or_bytes.seek(0)
                    data_dict = json.load(path_or_bytes)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

            if data_dict and data_dict.get('asset', {}).get('version') == '2.0':
                return 'gltf'

        return False

    @staticmethod
    def load(data_or_path, folder=None, filename=None, repair=False, ignore_http_uri=False):
        loaded_glb = False
        if type(data_or_path) is dict:
            data = data_or_path
        else:
            if type(data_or_path) is str:
                parts = data_or_path.split('/')
                filename = '.'.join(parts[-1].split('.')[:-1])
                folder = '/'.join(parts[:-1])
                with open(data_or_path, 'rb') as f:
                    file_buffer = BytesIO(f.read())
            elif isinstance(data_or_path, (bytes, bytearray)):
                file_buffer = BytesIO(data_or_path)
            elif type(data_or_path) is BytesIO:
                file_buffer = data_or_path
            else:
                raise ValueError('Can not load object of type ' + type(data_or_path))

            file_buffer.seek(0)
            magic, glb_version, file_size = np.frombuffer(file_buffer.read(12), dtype='uint32')
            if magic == GLTF.MAGIC:
                if glb_version != 2:
                    raise NotImplementedError('Only glb version 2 is supported!')
                total_bytes_read = 12
                while True:
                    header_bytes = file_buffer.read(8)
                    if not header_bytes:
                        if total_bytes_read != file_size:
                            raise ValueError('Expected ' + file_size + ' bytes' +
                                             ' but only read ' + total_bytes_read)
                        break
                    total_bytes_read += 8
                    chunk_size, chunk_type = np.frombuffer(header_bytes, dtype='uint32')
                    chunk = file_buffer.read(int(chunk_size))
                    total_bytes_read += chunk_size
                    if chunk_type == GLTF.JSON_CHUNK:
                        data = json.loads(chunk.decode('utf-8'))
                    elif chunk_type == GLTF.BINARY_CHUNK:
                        buffer = data['buffers'][0]
                        buffer['data'] = bytearray(chunk)[:buffer['byteLength']]
                    else:
                        raise TypeError('Invalid chunk type: ' + chunk_type)
                loaded_glb = True

            else:
                file_buffer.seek(0)
                data = json.loads(file_buffer.read().decode('utf-8'))

        gltf = GLTF(folder, filename, loaded_glb)
        gltf.ignore_http_uri = ignore_http_uri

        asset = data.get('asset', {})
        gltf.asset.update(extras=asset.get('extras', {}))

        extensions = data.get('extensionsUsed')
        if extensions:
            gltf.extensions_used = extensions

        for buf in data.get('buffers', []):
            gltf.buffers.append(Buffer(buf, gltf))

        for bv in data.get('bufferViews', []):
            gltf.buffer_views.append(BufferView(bv, gltf))

        for img in data.get('images', []):
            gltf.images.append(Image(img, gltf))

        for acc in data.get('accessors', []):
            if acc['type'] == 'SCALAR':
                acc = ScalarArray(acc, gltf)
            elif acc['type'] == 'VEC3':
                acc = Vec3Array(acc, gltf)
            elif acc['type'] == 'VEC2':
                acc = Vec2Array(acc, gltf)
            elif acc['type'] == 'VEC4':
                acc = Vec4Array(acc, gltf)
            elif acc['type'] == 'MAT4':
                acc = Mat4Array(acc, gltf)
            else:
                raise NotImplementedError('Accessor of type ' + acc['type'] + ' not implemented')
            gltf.accessors.append(acc)

        for sam in data.get('samplers', []):
            gltf.samplers.append(Sampler(sam))

        for tex in data.get('textures', []):
            gltf.textures.append(Texture(tex, gltf))

        for mat in data.get('materials', []):
            gltf.materials.append(Material(mat, gltf))

        for mesh in data.get('meshes', []):
            gltf.meshes.append(Mesh(mesh, gltf))

        for camera in data.get('cameras', []):
            gltf.cameras.append(Camera(camera))

        nodes = data.get('nodes', [])
        for node in nodes:
            gltf.nodes.append(Node(node, gltf))

        for skin in data.get('skins', []):
            gltf.skins.append(Skin(skin, gltf))

        for node, node_dict in zip(gltf.nodes, nodes):
            children = node_dict.get('children', [])
            node.find_children(children, gltf)
            # skins reference nodes, so a node's skin must be referenced afterwards
            # in order to avoid the circular dependency
            if 'skin' in node_dict:
                node.skin = gltf.skins[node_dict['skin']]

        for anim in data.get('animations', []):
            gltf.animations.append(Animation(anim, gltf))

        for scene in data.get('scenes', []):
            gltf.scenes.append(Scene(scene, gltf))

        scene_idx = data.get('scene')
        if scene_idx is not None:
            gltf.scene = gltf.scenes[scene_idx]

        if repair:
            gltf.repair()

        return gltf

    def add_root_transform(self, transform):
        root_nodes = self.get_root_nodes()
        if len(root_nodes) == 1 and root_nodes[0].name == 'RootTransform':
            root = root_nodes[0]
        else:
            root = Node(name='RootTransform', children=root_nodes)
            self.nodes.append(root)
            if self.scene:
                self.scene.nodes = [root]
        if root.matrix is not None:
            transform = root.matrix.dot(transform)
        root.matrix = transform

    def get_bounding_box(self):
        g = self.copy()
        g.apply_all_transforms()
        g_max = [0, 0, 0]
        g_min = [0, 0, 0]
        for m in g.meshes:
            for p in m.primitives:
                p_max = p.positions.max
                g_max[0] = max(g_max[0], p_max[0])
                g_max[1] = max(g_max[1], p_max[1])
                g_max[2] = max(g_max[2], p_max[2])
                p_min = p.positions.min
                g_min[0] = min(g_min[0], p_min[0])
                g_min[1] = min(g_min[1], p_min[1])
                g_min[2] = min(g_min[2], p_min[2])

        return tuple(_max - _min for _max, _min in zip(g_max, g_min))

    def copy(self):
        return GLTF.load(self.render())

    def render(self, binary=False, embed=None, split_to=None):
        if embed is None:
            embed = binary and not split_to
        self.buffers = []
        self.buffer_views = []

        data = {
            'asset': self.asset,
            'buffers': [],
            'bufferViews': [],
        }

        if self.scene:
            data['scene'] = self.index('scenes', self.scene)

        if self.scenes:
            data['scenes'] = [s.render(self) for s in self.scenes]

        if self.animations:
            data['animations'] = [a.render(self) for a in self.animations]

        if self.skins:
            data['skins'] = [s.render(self) for s in self.skins]

        if self.nodes:
            data['nodes'] = [n.render(self) for n in self.nodes]

        if self.meshes:
            data['meshes'] = [m.render(self) for m in self.meshes]

        if self.cameras:
            data['cameras'] = [c.render() for c in self.cameras]

        if self.extensions_used:
            data['extensionsUsed'] = self.extensions_used

        if self.materials:
            data['materials'] = [mat.render(self) for mat in self.materials]

        if self.textures:
            data['textures'] = [tex.render(self) for tex in self.textures]

        if self.samplers:
            data['samplers'] = [sampler.render() for sampler in self.samplers]

        buffer = Buffer()

        if self.accessors:
            data['accessors'] = [acc.render(buffer, self) for acc in self.accessors]

        if self.images:
            data['images'] = [img.render(buffer, self, embed, split_to, splitting=bool(split_to))
                              for img in self.images]

        for bv in self.buffer_views:
            bv.write_to_buffer()
            data['bufferViews'].append(bv.render(self))

        data['buffers'].append(buffer.render())
        if split_to:
            buffer_filename = os.path.basename(split_to) + '.bin'
            with open(split_to + '.bin', 'wb') as f:
                f.write(data['buffers'][0].pop('data'))
            data['buffers'][0]['uri'] = buffer_filename

        if binary:
            for buf in data['buffers'][1:]:
                if not buf.get('uri'):
                    raise ValueError('GLB only supports one embedded buffer')

            total_size = 0

            binary_chunk = b''
            if not data['buffers'][0].get('uri'):
                binary_chunk = bytearray(data['buffers'][0].pop('data', b''))

            json_chunk = bytearray(json.dumps(data).encode())
            if len(json_chunk) % 4:
                # pad to 4 bytes with spaces
                json_chunk.extend(bytes([0x20] * (4 - len(json_chunk) % 4)))

            json_header = np.array([
                len(json_chunk),
                self.JSON_CHUNK,
            ], dtype='uint32').tobytes()

            total_size += len(json_header) + len(json_chunk)

            binary_header = b''
            if binary_chunk:
                if len(binary_chunk) % 4:
                    # pad to 4 bytes with zeroes
                    binary_chunk.extend(bytes([0x00] * (4 - len(binary_chunk) % 4)))
                binary_header = np.array([
                    len(binary_chunk),
                    self.BINARY_CHUNK,
                ], dtype='uint32').tobytes()

            total_size += len(binary_header) + len(binary_chunk)

            file_header = np.array([
                self.MAGIC,
                2,  # GLB container version
                total_size + 12,  # size of entire file (total_size + file_header length)
            ], dtype='uint32').tobytes()

            return bytearray(
                file_header +
                json_header +
                json_chunk +
                binary_header +
                binary_chunk
            )

        for buffer in data['buffers']:
            if not buffer.get('uri'):
                buffer['uri'] = binary_to_uri(buffer.pop('data'))

        return data

    def split_transparent_prims(self):
        for n in self.nodes:
            if not n.mesh:
                continue
            new_prims = []
            for prim in n.mesh.primitives:
                if prim.material and prim.material.alpha_mode is not None \
                        and prim.material.alpha_mode != Material.AlphaMode.OPAQUE \
                        and prim.texcoords:
                    new_prim = prim.split_transparency()
                    if new_prim:
                        new_prims.append(new_prim)
            n.mesh.primitives.extend(new_prims)

    def duplicate_shared_meshes(self):
        existing_meshes = []
        existing_accessors = []
        for n in self.nodes:
            if not n.mesh:
                continue
            if n.mesh in existing_meshes:
                n.mesh = Mesh(n.mesh.render(self), gltf=self)
                for p in n.mesh.primitives:
                    if p.positions:
                        p.positions = Vec3Array(p.positions.data)
                        self.accessors.append(p.positions)
                    if p.normals:
                        p.normals = Vec3Array(p.normals.data)
                        self.accessors.append(p.normals)
                self.meshes.append(n.mesh)
            else:
                for p in n.mesh.primitives:
                    if p.positions:
                        if p.positions in existing_accessors:
                            p.positions = Vec3Array(p.positions.data)
                            self.accessors.append(p.positions)
                        else:
                            existing_accessors.append(p.positions)
                    if p.normals:
                        if p.normals in existing_accessors:
                            p.normals = Vec3Array(p.normals.data)
                            self.accessors.append(p.normals)
                        else:
                            existing_accessors.append(p.normals)

            existing_meshes.append(n.mesh)

    def get_root_nodes(self):
        root_nodes = {
            id(n): n for n in self.nodes
        }

        for n in self.nodes:
            for child in n.children:
                if id(child) in root_nodes:
                    del root_nodes[id(child)]
        return list(root_nodes.values())

    def apply_all_transforms(self, transform=None, rotation=None):
        self.duplicate_shared_meshes()
        for n in self.get_root_nodes():
            n.apply_transforms(transform, rotation)
        self.repair()

    @staticmethod
    def remove_duplicates(input_list):
        trimmed_list = []
        for item in input_list:
            if item not in trimmed_list:
                trimmed_list.append(item)
        return trimmed_list

    def save(self, path_or_filename=None, bytesio=None, binary=None, split=False, **kwargs):
        folder = (self.folder or '.') + '/'
        filename = None
        if path_or_filename and not bytesio:
            if path_or_filename.endswith('.glb') and binary is None:
                binary = True
            if os.path.dirname(path_or_filename):
                folder = os.path.dirname(path_or_filename)
                if os.path.basename(path_or_filename):
                    filename = os.path.basename(path_or_filename)
            else:
                filename = path_or_filename
        elif binary is None:
            binary = self.default_to_glb

        if not filename and not bytesio:
            if not self.filename:
                raise ValueError('Filename required to save')
            filename = self.filename + ('.glb' if binary else '.gltf')

        if split:
            if bytesio:
                raise ValueError('Can not save in memory and also split out files')
            kwargs['split_to'] = os.path.join(folder, filename.split('.')[0])
        data = self.render(binary=binary, **kwargs)

        if bytesio:
            if binary:
                bytesio.write(data)
            else:
                json.dump(data, bytesio, sort_keys=True, indent=4, separators=(',', ': '))
            return bytesio

        path = os.path.join(folder, filename)
        if binary:
            with open(path, 'wb') as f:
                f.write(data)
        else:
            with open(path, 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))
        return path

    def repair(self):
        """Runs `ops.repair` on this file."""
        ops.repair(self)

    def center(self):
        """Runs `ops.center` on this file."""
        ops.center(self)
