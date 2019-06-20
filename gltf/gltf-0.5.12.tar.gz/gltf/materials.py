import os
import re
import math
import logging
import imghdr
import shutil
from enum import Enum
from uuid import uuid4
from io import BytesIO

import numpy as np
import requests
from PIL import Image as PImage

from .utils import BaseGLTFStructure, load_uri

logger = logging.getLogger(__name__)


class Image(object):
    name = ''
    _data = None
    mime_type = None
    gltf = None

    def __init__(self, image, gltf=None):
        if gltf:
            self.gltf = gltf

        if type(image) == dict:
            self.name = image.get('name', '')
            try:
                if 'bufferView' in image:
                    bv = gltf.buffer_views[image['bufferView']]
                    self.data = bv.data
                else:
                    self.data = image['uri']
            except KeyError:
                logger.warning('Image has no bufferView or uri')
        elif isinstance(image, PImage.Image):
            img_bytes = BytesIO()
            if len(image.getbands()) == 4:
                image.save(img_bytes, format='png')
            else:
                image.save(img_bytes, format='jpeg', quality=95)
            self.data = img_bytes.getvalue()
        else:
            self.data = image

    def __repr__(self):
        return self.name or super(Image, self).__repr__()

    def __eq__(self, other):
        if not isinstance(other, type(self)) or self.is_uri != other.is_uri:
            return False
        return (self.name, self.data) == (other.name, other.data)

    def __hash__(self):
        return hash(self.path or id(self))

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        mime_type = None
        try:
            str_type = unicode
        except NameError:
            str_type = str
        if type(data) is str_type:
            if data.startswith('data:'):
                data = load_uri(data)
            elif data.startswith('http'):
                if not self.gltf.ignore_http_uri:
                    r = requests.get(data)
                    if r.status_code >= 400:
                        logger.warning('Unable to fetch image uri')
                    else:
                        data = r.content
            else:
                data = data.replace('\\', '/')
                if os.path.isabs(data):
                    logger.warning('Image uri is an absolute path: ' + data)
                path = (os.path.join(self.gltf.folder, data)
                        if self.gltf and self.gltf.folder
                        else data)
                if os.path.exists(path):
                    mime_type = imghdr.what(path)
                else:
                    logger.warning('Image uri does not exist: ' + path)

        # Check type again in case a data uri was loaded above
        if type(data) is not str_type:
            mime_type = imghdr.what(None, data)
            if not mime_type:
                im = PImage.open(BytesIO(data))
                img_bytes = BytesIO()
                if len(im.getbands()) == 4:
                    im.save(img_bytes, format='PNG')
                else:
                    im.save(img_bytes, format='JPEG')

                data = img_bytes.getvalue()
                mime_type = imghdr.what(None, data)

        if mime_type:
            self.mime_type = 'image/' + mime_type
        else:
            logger.warning('Image format not recognized')

        self._data = data

    @property
    def is_uri(self):
        return type(self._data) is str

    @property
    def path(self):
        if not self.is_uri:
            return
        if self.gltf and self.gltf.folder:
            return os.path.join(self.gltf.folder, self.data)
        return self.data

    def get_fp(self):
        if self.is_uri:
            with open(self.path, 'rb') as f:
                return BytesIO(f.read())

        return BytesIO(self.data)

    def set_uri_to(self, folder):
        data = self.data
        if self.is_uri:
            data = self.get_fp().getvalue()

        for file in os.listdir(folder):
            with open(os.path.join(folder, file), 'rb') as f:
                file_bytes = f.read()
                if file_bytes == data:
                    self.data = os.path.join(folder, file)
                    break
        else:
            self.data = self.write_to(folder)

    def write_to(self, folder, name=None):
        if self.is_uri:
            filename = name or os.path.basename(self.data)
            shutil.copy(self.path, os.path.join(folder, filename))
            return filename

        filename = name or self.name or str(uuid4())[:8]
        if '.' in filename:
            ext = '.' + filename.split('.')[-1]
            filename = '.'.join(filename.split('.')[:-1])
        else:
            ext = '.'
            if self.mime_type == 'image/jpeg':
                ext += 'jpg'
            else:
                ext += self.mime_type.split('/')[-1]

        clean_filename = str(filename + ext).strip().replace(' ', '_')
        clean_filename = re.sub(r'(?u)[^-\w.]', '', clean_filename)

        path = os.path.join(folder, clean_filename)
        if os.path.exists(path) and name is None:
            filename = str(uuid4())[:8]
            path = os.path.join(folder, filename + ext)

        with open(path, 'wb') as f:
            f.write(self.data)

        return path

    def render(self, buffer, gltf, embed=False, write_to=None, splitting=False):
        image = {}
        if self.name:
            image['name'] = self.name

        data = self.data

        if not data:
            return image
        if self.mime_type is not None:
            image['mimeType'] = self.mime_type

        if write_to:
            folder = os.path.dirname(write_to)
            name = os.path.basename(write_to)
            image['uri'] = self.write_to(folder, name + str(gltf.images.index(self)))
            if splitting:
                image['uri'] = os.path.basename(image['uri'])
            return image

        if self.is_uri:
            if embed:
                try:
                    data = load_uri(self.data, folder=gltf.folder)
                except FileNotFoundError:
                    logger.error('Unable to load image uri: ' + self.data)
                    img_bytes = BytesIO()
                    PImage.new('RGB', (1, 1)).save(img_bytes, 'JPEG')
                    data = img_bytes.getvalue()
            else:
                image['uri'] = self.data
                return image

        view = buffer.get_view(image=self)
        if view.data:
            if view.byte_length != len(data):
                raise ValueError('Buffer view already exists for this image, '
                                 'but the byte_length does not match')
        else:
            view.write(data)
        image['bufferView'] = gltf.index('buffer_views', view)
        return image


class Sampler(BaseGLTFStructure):
    mag_filter = None
    min_filter = None
    wrap_s = None
    wrap_t = None

    class MagFilter(Enum):
        NEAREST = 9728
        LINEAR = 9729

    class MinFilter(Enum):
        NEAREST = 9728
        LINEAR = 9729
        NEAREST_MIPMAP_NEAREST = 9984
        LINEAR_MIPMAP_NEAREST = 9985
        NEAREST_MIPMAP_LINEAR = 9986
        LINEAR_MIPMAP_LINEAR = 9987

    class WrapMode(Enum):
        CLAMP_TO_EDGE = 33071
        MIRRORED_REPEAT = 33648
        REPEAT = 10497

    def __init__(self, sampler=None, name=None,
                 mag_filter=None, min_filter=None, wrap_s=None, wrap_t=None):
        if sampler:
            mag_filter = sampler.get('magFilter', mag_filter)
            if mag_filter:
                self.mag_filter = self.MagFilter(mag_filter)
            min_filter = sampler.get('minFilter', min_filter)
            if min_filter:
                self.min_filter = self.MinFilter(min_filter)
            wrap_s = sampler.get('wrapS', wrap_s)
            if wrap_s:
                self.wrap_s = self.WrapMode(wrap_s)
            wrap_t = sampler.get('wrapT', wrap_t)
            if wrap_t:
                self.wrap_t = self.WrapMode(wrap_t)
            self.name = sampler.get('name')
        else:
            self.name = name
            self.mag_filter = mag_filter
            self.min_filter = min_filter
            self.wrap_s = wrap_s
            self.wrap_t = wrap_t

    def __repr__(self):
        return self.name or super(Sampler, self).__repr__()

    def render(self):
        sampler = {}
        if self.name:
            sampler['name'] = self.name
        if self.mag_filter:
            sampler['magFilter'] = self.mag_filter.value
        if self.min_filter:
            sampler['minFilter'] = self.min_filter.value
        if self.wrap_s:
            sampler['wrapS'] = self.wrap_s.value
        if self.wrap_t:
            sampler['wrapT'] = self.wrap_t.value
        return sampler

    @staticmethod
    def wrap(val, wrap_mode):
        if 0 <= val <= 1:
            return val
        if wrap_mode == Sampler.WrapMode.CLAMP_TO_EDGE:
            return 1.0 if val > 1 else 0.0
        if wrap_mode == Sampler.WrapMode.REPEAT:
            portion, _ = math.modf(val)
            return portion if val > 0 else 1.0 + portion
        if wrap_mode == Sampler.WrapMode.MIRRORED_REPEAT:
            portion, whole = math.modf(abs(val))
            if (whole + 1) % 2:
                return portion
            return 1.0 - portion
        raise TypeError('Invalid WrapMode')

    def wrap_point(self, point):
        return (
            self.wrap(point[0], self.wrap_s or self.WrapMode.REPEAT),
            self.wrap(point[1], self.wrap_t or self.WrapMode.REPEAT)
        )


class Texture(BaseGLTFStructure):
    sampler = None
    source = None

    def __init__(self, texture=None, gltf=None, name=None,
                 image=None, sampler=None, mirrored_repeat=False, repeat=False):
        if texture:
            sam = texture.get('sampler')
            if sam is not None:
                self.sampler = sam if isinstance(sam, Sampler) else gltf.samplers[sam]
            img = texture.get('source')
            if img is not None:
                self.source = img if isinstance(img, Image) else gltf.images[img]
            self.name = texture.get('name')
        else:
            self.name = name
            self.sampler = sampler
            if mirrored_repeat:
                self.sampler = Sampler(wrap_s=Sampler.WrapMode.MIRRORED_REPEAT,
                                       wrap_t=Sampler.WrapMode.MIRRORED_REPEAT)
            if repeat:
                self.sampler = Sampler(wrap_s=Sampler.WrapMode.REPEAT,
                                       wrap_t=Sampler.WrapMode.REPEAT)
            if image:
                self.source = image if isinstance(image, Image) else Image(image)

    def __repr__(self):
        return self.name or super(Texture, self).__repr__()

    def render(self, gltf):
        texture = {'source': gltf.index('images', self.source)}
        if self.name:
            texture['name'] = self.name
        if self.sampler:
            texture['sampler'] = gltf.index('samplers', self.sampler)
        return texture


class Material(BaseGLTFStructure):
    alpha_mode = None
    double_sided = None
    base_color_factor = None
    color_texture = None
    color_uv = None
    color_extensions = None
    rough_metal_texture = None
    rough_uv = None
    rough_metal_extensions = None
    normal_texture = None
    normal_uv = None
    normal_scale = None
    normal_extensions = None
    occlusion_texture = None
    occlusion_uv = None
    occlusion_strength = None
    occlusion_extensions = None
    emissive_texture = None
    emissive_factor = None
    emissive_uv = None
    emissive_extensions = None
    metallic_factor = None
    roughness_factor = None

    diffuse_factor = None
    specular_factor = None
    glossiness_factor = None
    diffuse_texture = None
    spec_gloss_texture = None

    class AlphaMode(Enum):
        OPAQUE = 'OPAQUE'
        MASK = 'MASK'
        BLEND = 'BLEND'

    def __init__(self, material=None, gltf=None, name=None, image=None,
                 base_color_factor=None, double_sided=None,
                 color_texture=None, color_uv=None,
                 normal_texture=None, normal_uv=None,
                 occlusion_texture=None, occlusion_uv=None,
                 emissive_texture=None, emissive_uv=None,
                 rough_metal_texture=None, rough_uv=None,
                 alpha_mode=None, metallic_factor=0, roughness_factor=None, emissive_factor=None,
                 diffuse_factor=None, specular_factor=None, glossiness_factor=None,
                 diffuse_texture=None, spec_gloss_texture=None):
        if material:
            self.name = material.get('name')
            if material.get('alphaMode'):
                self.alpha_mode = self.AlphaMode(material.get('alphaMode'))
            if material.get('doubleSided'):
                self.double_sided = material.get('doubleSided')
            self.emissive_factor = material.get('emissiveFactor')
            pbr = material.get('pbrMetallicRoughness')
            if pbr:
                self.base_color_factor = pbr.get('baseColorFactor')
                self.metallic_factor = pbr.get('metallicFactor')
                self.roughness_factor = pbr.get('roughnessFactor')

                base_color_texture = pbr.get('baseColorTexture')
                if base_color_texture:
                    self.color_texture = gltf.textures[base_color_texture['index']]
                    if 'texCoord' in base_color_texture:
                        self.color_uv = base_color_texture['texCoord']
                    if 'extensions' in base_color_texture:
                        self.color_extensions = base_color_texture['extensions']

                metallic_roughness_tex = pbr.get('metallicRoughnessTexture')
                if metallic_roughness_tex:
                    self.rough_metal_texture = gltf.textures[metallic_roughness_tex['index']]
                    if 'texCoord' in metallic_roughness_tex:
                        self.rough_uv = metallic_roughness_tex['texCoord']
                    if 'extensions' in metallic_roughness_tex:
                        self.rough_metal_extensions = metallic_roughness_tex['extensions']

            normal = material.get('normalTexture')
            if normal:
                if 'index' in normal:
                    self.normal_texture = gltf.textures[normal['index']]
                if 'texCoord' in normal:
                    self.normal_uv = normal['texCoord']
                if 'scale' in normal:
                    self.normal_scale = normal['scale']
                if 'extensions' in normal:
                    self.normal_extensions = normal['extensions']

            occlusion = material.get('occlusionTexture')
            if occlusion:
                if 'index' in occlusion:
                    self.occlusion_texture = gltf.textures[occlusion['index']]
                if 'texCoord' in occlusion:
                    self.occlusion_uv = occlusion['texCoord']
                if 'strength' in occlusion:
                    self.occlusion_strength = occlusion['strength']
                if 'extensions' in occlusion:
                    self.occlusion_extensions = occlusion['extensions']

            emissive = material.get('emissiveTexture')
            if emissive:
                if 'index' in emissive:
                    self.emissive_texture = gltf.textures[emissive['index']]
                if 'texCoord' in emissive:
                    self.emissive_uv = emissive['texCoord']
                if 'extensions' in emissive:
                    self.emissive_extensions = emissive['extensions']

            extensions = material.get('extensions')
            if extensions:
                spec_gloss = extensions.get('KHR_materials_pbrSpecularGlossiness')
                if spec_gloss:
                    self.diffuse_factor = spec_gloss.get('diffuseFactor')
                    self.specular_factor = spec_gloss.get('specularFactor')
                    self.glossiness_factor = spec_gloss.get('glossinessFactor')
                    diffuse_texture = spec_gloss.get('diffuseTexture')
                    if diffuse_texture and diffuse_texture.get('index') is not None:
                        self.diffuse_texture = gltf.textures[diffuse_texture['index']]
                    spec_gloss_texture = spec_gloss.get('specularGlossinessTexture')
                    if spec_gloss_texture and spec_gloss_texture.get('index') is not None:
                        self.spec_gloss_texture = gltf.textures[spec_gloss_texture['index']]
        else:
            self.name = name
            self.double_sided = double_sided
            self.base_color_factor = base_color_factor
            self.color_texture = color_texture
            self.color_uv = color_uv
            self.normal_texture = normal_texture
            self.normal_uv = normal_uv
            self.occlusion_texture = occlusion_texture
            self.occlusion_uv = occlusion_uv
            self.rough_metal_texture = rough_metal_texture
            self.rough_uv = rough_uv
            self.emissive_texture = emissive_texture
            self.emissive_uv = emissive_uv
            self.metallic_factor = metallic_factor
            self.roughness_factor = roughness_factor
            self.emissive_factor = emissive_factor
            self.diffuse_factor = diffuse_factor
            self.specular_factor = specular_factor
            self.glossiness_factor = glossiness_factor
            self.diffuse_texture = diffuse_texture
            self.spec_gloss_texture = spec_gloss_texture
            if alpha_mode:
                self.alpha_mode = self.AlphaMode(alpha_mode)
            if image:
                self.color_texture = Texture(image=image)

    def __repr__(self):
        return self.name or super(Material, self).__repr__()

    def __hash__(self):
        return id(self)

    def __contains__(self, item):
        return (self.color_texture == item or
                self.rough_metal_texture == item or
                self.normal_texture == item or
                self.emissive_texture == item or
                self.diffuse_texture == item or
                self.spec_gloss_texture == item)

    def render(self, gltf):
        material = {'pbrMetallicRoughness': {}}

        if self.color_texture:
            color_texture = {
                'index': gltf.index('textures', self.color_texture)
            }
            if self.color_uv is not None:
                color_texture['texCoord'] = self.color_uv
            if self.color_extensions:
                color_texture['extensions'] = self.color_extensions
            material['pbrMetallicRoughness']['baseColorTexture'] = color_texture

        if self.rough_metal_texture:
            rough_metal_texture = {
                'index': gltf.index('textures', self.rough_metal_texture)
            }
            if self.rough_uv is not None:
                rough_metal_texture['texCoord'] = self.rough_uv
            if self.rough_metal_extensions:
                rough_metal_texture['extensions'] = self.rough_metal_extensions
            material['pbrMetallicRoughness']['metallicRoughnessTexture'] = rough_metal_texture

        if self.normal_texture:
            normal_texture = {
                'index': gltf.index('textures', self.normal_texture)
            }
            if self.normal_uv is not None:
                normal_texture['texCoord'] = self.normal_uv
            if self.normal_scale is not None:
                normal_texture['scale'] = self.normal_scale
            if self.normal_extensions:
                normal_texture['extensions'] = self.normal_extensions
            material['normalTexture'] = normal_texture

        if self.occlusion_texture:
            occlusion_texture = {
                'index': gltf.index('textures', self.occlusion_texture)
            }
            if self.occlusion_uv is not None:
                occlusion_texture['texCoord'] = self.occlusion_uv
            if self.occlusion_strength is not None:
                occlusion_texture['strength'] = self.occlusion_strength
            if self.occlusion_extensions:
                occlusion_texture['extensions'] = self.occlusion_extensions
            material['occlusionTexture'] = occlusion_texture

        if self.emissive_texture:
            emissive_texture = {
                'index': gltf.index('textures', self.emissive_texture)
            }
            if self.emissive_uv is not None:
                emissive_texture['texCoord'] = self.emissive_uv
            if self.emissive_extensions:
                emissive_texture['extensions'] = self.emissive_extensions
            material['emissiveTexture'] = emissive_texture

        if self.name:
            material['name'] = self.name
        if self.alpha_mode:
            material['alphaMode'] = self.alpha_mode.value
        if self.double_sided:
            material['doubleSided'] = self.double_sided
        if self.emissive_factor:
            material['emissiveFactor'] = self.emissive_factor
        if self.metallic_factor is not None:
            material['pbrMetallicRoughness']['metallicFactor'] = self.metallic_factor
        if self.roughness_factor is not None:
            material['pbrMetallicRoughness']['roughnessFactor'] = self.roughness_factor
        if self.base_color_factor:
            material['pbrMetallicRoughness']['baseColorFactor'] = self.base_color_factor

        spec_gloss = {}
        if self.diffuse_texture:
            spec_gloss['diffuseTexture'] = {'index': gltf.index('textures', self.diffuse_texture)}
        if self.spec_gloss_texture:
            spec_gloss['specularGlossinessTexture'] = {
                'index': gltf.index('textures', self.spec_gloss_texture)
            }
        if self.glossiness_factor is not None:
            spec_gloss['glossinessFactor'] = self.glossiness_factor
        if self.diffuse_factor:
            spec_gloss['diffuseFactor'] = self.diffuse_factor
        if self.specular_factor:
            spec_gloss['specularFactor'] = self.specular_factor
        if spec_gloss:
            material['extensions'] = {'KHR_materials_pbrSpecularGlossiness': spec_gloss}
            if 'KHR_materials_pbrSpecularGlossiness' not in gltf.extensions_used:
                gltf.extensions_used.append('KHR_materials_pbrSpecularGlossiness')

        if not material['pbrMetallicRoughness']:
            material.pop('pbrMetallicRoughness')
        return material

    def repair(self):
        if self.emissive_factor and isinstance(self.emissive_factor, list):
            new_emissive = []
            for f in self.emissive_factor:
                if type(f) is str:
                    f = float(f)
                if f < 0:
                    f = 0
                if f > 1:
                    f = 1
                new_emissive.append(f)
            self.emissive_factor = new_emissive
        if self.base_color_factor and isinstance(self.base_color_factor, list):
            new_color = []
            for f in self.base_color_factor:
                if type(f) is str:
                    f = float(f)
                if f < 0:
                    f = 0
                if f > 1:
                    f = 1
                new_color.append(f)
            self.base_color_factor = new_color

        # Fix VALUE_NOT_IN_RANGE errors
        if self.roughness_factor:
            self.roughness_factor = np.clip(self.roughness_factor, 0, 1.0)
        if self.metallic_factor:
            self.metallic_factor = np.clip(self.metallic_factor, 0, 1.0)
        if self.normal_scale:
            self.normal_scale = np.clip(self.normal_scale, -1.0, 1.0)
