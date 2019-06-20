"""
Easily load and operate on GLTF files with this library.

```python
from gltf import GLTF

model = GLTF.load("input.glb")
model.repair()
model.save("output.glb")
```

Useful operations exist in the `ops` module.
"""

from .gltf import GLTF, Scene
from .animations import Animation, Skin
from .buffers import Buffer, BufferView, Vec2Array, Vec3Array, Vec4Array, ScalarArray, Mat4Array
from .materials import Material, Texture, Sampler, Image
from .nodes import Node, Mesh, Primitive
