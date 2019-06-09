#!/usr/bin/env python
# -*- coding: utf-8
import logging
import re
import tempfile
from collections import namedtuple

from .image import Image

LOG = logging.getLogger(__name__)

FROM_PATTERN = re.compile(r"FROM\s+(?P<name>[\w./-]+)(:(?P<tag>[\w.-]+))?(\s+(?:AS|as) (?P<alias>\w+))?")
ARCH_PATTERN = re.compile(r"# dockerma archs:(?P<archs>.+):")

# Map from docker archs to monsonnl/qemu-wrap-build-files
SUPPORTED_ARCHS = {
    "amd64": "x86_64",
    "arm": "arm32v7",
    "arm64": "arm64v8",
}


def _parse_archs(line):
    m = ARCH_PATTERN.match(line)
    if m:
        archs = m.group("archs")
        return re.split(r"\s*,\s*", archs)
    return tuple()


class Builder(object):
    name = "build"

    def __init__(self, parser):
        parser.add_argument("-f", "--file", help="Name of the Dockerfile", default="Dockerfile")
        parser.add_argument("-t", "--tag", action="append", help="Name and optionally a tag in the 'name:tag' format")
        parser.add_argument("path", help="Docker context", metavar="PATH|URL")
        self._docker = None
        self._options = None
        self._remaining = []
        self._base_images = {}
        self._alias_lookup = {}
        self._archs = set()
        self._template = [BuildToolStage()]
        self._work_dir = namedtuple("_", ["name"])(None)

    def __call__(self, docker, options, remaining_args):
        self._secondary_init(docker, options, remaining_args)
        self._parse_dockerfile()
        self._check_for_problems()
        for arch in self._archs:
            self._build(arch)

    def _secondary_init(self, docker, options, remaining_args):
        self._docker = docker
        self._options = options
        self._remaining = remaining_args
        if not self._options.debug:
            self._work_dir = tempfile.TemporaryDirectory(prefix="dockerma-")

    def _check_for_problems(self):
        if not self._archs.issubset(SUPPORTED_ARCHS.keys()):
            missing = self._archs - SUPPORTED_ARCHS.keys()
            raise BuildError("dockerma does not support requested arch: {}".format(", ".join(missing)))
        for image in self._base_images.keys():
            if image.name in self._alias_lookup:
                continue
            if not self._archs.issubset(image.get_supported_archs()):
                missing = self._archs - image.get_supported_archs()
                raise BuildError("{} does not support requested arch: {}".format(image, ", ".join(missing)))

    def _parse_dockerfile(self):
        with open(self._options.file) as fobj:
            for line in fobj:
                try:
                    image = self._parse_from(line)
                    self._template.extend((FromMarker(image), CopyTools(), CrossBuild()))
                    self._base_images[image] = {}
                    if image.alias:
                        self._alias_lookup[image.alias] = image
                    continue
                except ValueError:
                    pass
                archs = _parse_archs(line)
                if archs:
                    self._archs.update(archs)
                    continue
                self._template.append(Identity(line))
        self._template.append(CrossBuild("end"))

    def _parse_from(self, line):
        m = FROM_PATTERN.match(line)
        if m:
            groups = m.groupdict()
            name = groups["name"]
            return Image(self._docker, name, groups["tag"], groups["alias"], name in self._alias_lookup)
        raise ValueError("Unable to parse image reference from line %r" % line)

    def _build(self, arch):
        LOG.info("Building image for %s", arch)
        dockerfile = tempfile.NamedTemporaryFile(mode="w+", suffix=".{}".format(arch),
                                                 prefix="Dockerfile-", dir=self._work_dir.name, delete=False)
        dockerfile.write("".join(r.render(arch) for r in self._template))
        dockerfile.flush()
        LOG.debug("Rendered {} for {}".format(dockerfile.name, arch))
        args = []
        for tag in self._options.tag:
            arch_tag = "{}-{}".format(tag, arch)
            args.extend(("-t", arch_tag))
        args.extend(("-f", dockerfile.name))
        args.extend(self._remaining)
        args.append(self._options.path)
        self._docker.execute("build", *args)


class Renderable(object):
    def render(self, arch):
        raise NotImplementedError()


class Identity(Renderable):
    def __init__(self, value):
        self._value = value

    def render(self, arch):
        return self._value


class FromMarker(Renderable):
    def __init__(self, image):
        self._image = image

    def render(self, arch):
        return "FROM {} AS {}\n".format(self._image.sha(arch), self._image.alias)


class BuildToolStage(Identity):
    def __init__(self):
        super(BuildToolStage, self).__init__("FROM monsonnl/qemu-wrap-build-files AS dockerma_build_files\n")


class CopyTools(Renderable):
    def render(self, arch):
        qemu_arch = SUPPORTED_ARCHS[arch]
        return "COPY --from=dockerma_build_files /cross-build/{}/bin /bin\n".format(qemu_arch)


class CrossBuild(Renderable):
    def __init__(self, kind="start"):
        self._kind = kind

    def render(self, arch):
        return "RUN [ \"cross-build-{}\" ]\n".format(self._kind)


class BuildError(Exception):
    pass
