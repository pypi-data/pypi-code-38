"""
Unofficial python library for reading and writing photoscan/metashape psx file format.
"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime

from json import dumps
import json
import os
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union
import warnings
from xml.etree.ElementTree import fromstring
import xml.etree.ElementTree as ET
from xml import etree
from zipfile import ZipFile


from dataclasses_json import dataclass_json
from lxml import etree
from PIL import Image as PILimage  # pillow package
from xmljson import gdata

__version__ = "0.1.0"
__version_psx__ = "1.2.0"


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError("Type %s not serializable" % type(obj))


@dataclass_json
@dataclass
class Thumbnails:
    camera_ids: List[str] = field(default_factory=list)
    thumb_paths: List[str] = field(default_factory=list)

    def xml(self):
        root = etree.Element("thumbnails", version=__version_psx__)
        for i, c in enumerate(self.camera_ids):
            root.append(etree.Element("thumbnail", camera_id=c, path=self.thumb_paths[i]))
        """
<?xml version="1.0" encoding="UTF-8"?>
<thumbnails version="1.2.0"/>
---
<?xml version="1.0" encoding="UTF-8"?>
<thumbnails version="1.2.0">
  <thumbnail camera_id="0" path="c0.jpg"/>
  <thumbnail camera_id="1" path="c1.jpg"/>
</thumbnails>

        """
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())


def generate_zip(obj, path, zipfname, extra_files=None):
    extra_files = extra_files if extra_files else []
    doc_file = path.joinpath("doc.xml")
    print(f"  save {doc_file}")
    obj.save(doc_file)
    zip_file = path.joinpath(zipfname)
    with ZipFile(zip_file, 'w') as fzip:
        for extra_file in extra_files:
            fzip.write(extra_file, arcname=Path(extra_file).name)
        fzip.write(doc_file, arcname="doc.xml")
    doc_file.unlink()
    for extra_file in extra_files:
        Path(extra_file).unlink()


@dataclass_json
@dataclass
class Property:
    name: str = ""
    value: str = ""
    text: str = None

    def xml(self):
        root = etree.Element("property", name=self.name, value=self.value)
        return root


@dataclass_json
@dataclass
class Photo:
    path: str = None
    meta: List[Property] = field(default_factory=list)

    def generate_meta(self):
        # generate meta properties
        file_size = os.stat(self.path).st_size
        mod_date = os.stat(self.path).st_mtime
        mod_date = datetime.utcfromtimestamp(mod_date).strftime('%Y-%m-%d %H:%M:%S')
        im = PILimage.open(self.path)
        width, height = im.size
        self.meta.append(Property(name="File/ImageHeight", value=str(height)))
        self.meta.append(Property(name="File/ImageWidth", value=str(width)))
        self.meta.append(Property(name="System/FileModifyDate", value=mod_date))
        self.meta.append(Property(name="System/FileSize", value=str(file_size)))

    def xml(self):
        root = etree.Element("photo", path=self.path)
        meta = etree.Element("meta")
        root.append(meta)
        for prop in self.meta:
            meta.append(prop.xml())
        """
      <photo path="../../../../../comparephotos/test/file0003_1.png">
        <meta>
          <property name="File/ImageHeight" value="1080"/>
          <property name="File/ImageWidth" value="1920"/>
          <property name="System/FileModifyDate" value="2019:04:08 19:29:32"/>
          <property name="System/FileSize" value="2336461"/>
        </meta>
      </photo>
        """
        return root


@dataclass_json
@dataclass
class FrameCamera:  # reduced version used in Chunk, full version used in Frame
    camera_id: int = None
    photo: Photo = None #List[Photo] = field(default_factory=list)

    def xml(self, camera_id=None):
        self.camera_id = camera_id if camera_id else self.camera_id
        root = etree.Element("camera", camera_id=camera_id)
        root.append(self.photo.xml())
        """        
    <camera camera_id="0">
      <photo path="../../../../../comparephotos/test/file0003_0.png">
        <meta>
          <property name="File/ImageHeight" value="1080"/>
          <property name="File/ImageWidth" value="1920"/>
          <property name="System/FileModifyDate" value="2019:04:08 19:29:29"/>
          <property name="System/FileSize" value="2257248"/>
        </meta>
      </photo>
    </camera>
        """
        return root


@dataclass_json
@dataclass
class ChunkCamera:  # reduced version used in Chunk
    id: int = None
    sensor_id: int = None
    label: str = None

    def xml(self, camera_id=None):
        self.id = camera_id if camera_id else self.id
        root = etree.Element("camera", id=str(self.id), sensor_id=str(self.sensor_id), label=self.label)
        return root


@dataclass_json
@dataclass
class Frame:
    cameras: List[FrameCamera] = field(default_factory=list)
    thumbnails: Thumbnails = None  #List[Thumbnail] = field(default_factory=list)

    def load_psx(self, fname):
        return self

    def xml(self):
        root = etree.Element("frame", version=__version_psx__)
        cameras = etree.Element("cameras")
        for i, camera in enumerate(self.cameras):
            warnings.warn("need to add camera_id to xml here.")
            cameras.append(camera.xml(camera_id=str(i)))
        """
<?xml version="1.0" encoding="UTF-8"?>
<frame version="1.2.0">
  <thumbnails path="thumbnails/thumbnails.zip"/>
</frame>
        """
        root.append(cameras)
        root.append(etree.Element("thumbnails", path="thumbnails/thumbnails.zip"))
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())

    def generate_psx(self, index, chunk_path):
        # chunk_path is the Pathlib object to the chunk directory
        frame_path = chunk_path.joinpath(f"{index}")
        print(f"  create frame {frame_path}")
        if not frame_path.is_dir():
            # create the chunk directory and the files in it.
            # a chunk.zip with a doc.xml inside it
            # and a frame? directory
            frame_path.mkdir()
        thumbnails_path = frame_path.joinpath("thumbnails")
        if not thumbnails_path.is_dir():
            thumbnails_path.mkdir()
        extra_files = []
        for c, camera in enumerate(self.cameras):
            im = PILimage.open(camera.photo.path)
            im.thumbnail((192, 108), PILimage.ANTIALIAS)
            p = thumbnails_path.joinpath(f"c{c}.jpg")
            im.save(p, "JPEG", optimize=True)
            extra_files.append(p.as_posix())
            self.thumbnails.camera_ids.append(str(c))
            self.thumbnails.thumb_paths.append(p.name)
        generate_zip(self.thumbnails, thumbnails_path, "thumbnails.zip", extra_files)

        generate_zip(self, frame_path, "frame.zip")


@dataclass_json
@dataclass
class Resolution:
    width: int = None
    height: int = None

    def xml(self):
        root = etree.Element("resolution", width=str(self.width), height=str(self.height))
        return root


@dataclass_json
@dataclass
class Band:
    label: str = None

    def xml(self):
        #  <band label="Red"/>
        return etree.Element("band", label=self.label)


@dataclass_json
@dataclass
class Sensor:
    label: str = None
    type: str = None
    resolution: Resolution = None
    properties: List[Property] = field(default_factory=list)
    bands: List[Band] = field(default_factory=list)
    data_type: str = None

    def xml(self, sensor_id):
        d = {"id": sensor_id}
        if self.type:
            d["type"] = self.type
        if self.label:
            d["label"] = self.label
        root = etree.Element("sensor", **d)
        root.append(self.resolution.xml())
        for property in self.properties:
            root.append(property.xml())

        bands = etree.Element("bands")
        for band in self.bands:
            bands.append(band.xml())
        root.append(bands)
        data_type = etree.Element("data_type")
        if self.data_type:
            data_type.text = self.data_type
            root.append(data_type)
        """
    <sensor id="0" label="unknown" type="frame">
      <resolution width="640" height="480"/>
      <property name="layer_index" value="0"/>
      <bands>
        <band label="Red"/>
        <band label="Green"/>
        <band label="Blue"/>
      </bands>
      <data_type>uint8</data_type>
    </sensor>
        """
        return root


@dataclass_json
@dataclass
class Settings:
    properties: List[Property] = field(default_factory=list)


@dataclass_json
@dataclass
class Chunk:
    name: str = None
    label: str = None
    enabled: bool = None
    version: str = ""
    sensors: List[Sensor] = field(default_factory=list)
    cameras: List[ChunkCamera] = field(default_factory=list)
    frames: List[Frame] = field(default_factory=list)
    reference: str = ""
    settings: List[Property] = field(default_factory=list)

    def defaults(self):
        self.settings.append(Property(name="accuracy_tiepoints", value="1"))
        self.settings.append(Property(name="accuracy_cameras", value="10"))
        self.settings.append(Property(name="accuracy_cameras_ypr", value="10"))
        self.settings.append(Property(name="accuracy_markers", value="0.005"))
        self.settings.append(Property(name="accuracy_scalebars", value="0.001"))
        self.settings.append(Property(name="accuracy_projections", value="0.1"))

    def load_psx(self, fname):
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError
        chunk = None
        with ZipFile(fpath, 'r') as zf:
            for chunkfname in zf.filelist:
                xmlstr = zf.read(chunkfname)
                bf = dumps(gdata.data(fromstring(xmlstr))["chunk"])
                j = json.loads(bf)
                chunk = Chunk(enabled=j["enabled"], label=j["label"], version=j["version"])
                #document = Document(version=j["version"], next_id=j["chunks"]["next_id"], active_id=j["chunks"]["active_id"])
                for key, data in j["sensors"].items():
                    if key == "sensor":
                        sensor = Sensor(
                                resolution=Resolution(**data["resolution"]),
                                type=data["type"],
                                label=data["label"])
                        if "property" in data:
                            sensor.properties.append(Property(**data["property"]))
                        chunk.sensors.append(sensor)

                for key, data in j["cameras"].items():
                    if key == "camera":
                        chunk.cameras.append(ChunkCamera(id=data["id"], sensor_id = data["sensor_id"], label=data["label"]))
#                        chunk.cameras[-1].photo.path = Path(chunk.cameras[-1].photo.path).relative_to(fpath).as_posix()

                if "settings" in j:
                    chunk.settings = Settings()

                for key, data in j["settings"].items():
                    if key == "property":
                        for prop in data:
                            chunk.settings.properties.append(Property(**prop))

                if "reference" in j:
                    chunk.reference = j["reference"].get("$t", None)

                for key, data in j["reference"].items():
                    if key == "property":
                        for prop in data:
                            chunk.settings.properties.append(Property(**prop))

                for key in j["frames"].keys():
                    if key == "frame":
                        frame_json = j["frames"][key]
                        cname = Path(fpath.parent, frame_json["path"])
                        chunk.frames.append(Frame().load_psx(cname))
        return chunk

    def xml(self):
        enabled = "true" if self.enabled else "false"
        if self.label:
            root = etree.Element("chunk", version=__version_psx__, enabled=enabled, label=self.label)
        else:
            root = etree.Element("chunk", version=__version_psx__, enabled=enabled)

        child_node = etree.Element("sensors", next_id=f"{len(self.sensors)}")
        for i, child in enumerate(self.sensors):
            child_xml = child.xml(sensor_id=str(i))  #etree.Element("sensor", id=f"{i}")
            child_node.append(child_xml)
        root.append(child_node)

        child_node = etree.Element("cameras", next_id=f"{len(self.cameras)}", next_group_id="0")
        warnings.warn("Not sure what chunk.cameras.next_group_id is for, defaulting to zero.")
        for i, child in enumerate(self.cameras):
            child_node.append(child.xml(i))
        root.append(child_node)

        child_node = etree.Element("frames", next_id=f"{len(self.frames)}")
        for i, child in enumerate(self.frames):
            child_xml = etree.Element("frame", id=f"{i}", path=f"{i}/frame.zip")
            child_node.append(child_xml)
        root.append(child_node)

        reference = etree.Element("reference")
        reference.text = 'LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
        root.append(reference)

        settings = etree.Element("settings")
        for property in self.settings:
            settings.append(property.xml())
        """
        settings.append(etree.Element("property", name="accuracy_tiepoints", value="1"))
        settings.append(etree.Element("property", name="accuracy_cameras", value="10"))
        settings.append(etree.Element("property", name="accuracy_cameras_ypr", value="10"))
        settings.append(etree.Element("property", name="accuracy_markers", value="0.005"))
        settings.append(etree.Element("property", name="accuracy_scalebars", value="0.001"))
        settings.append(etree.Element("property", name="accuracy_projections", value="0.1"))
        """
        root.append(settings)
        """
<?xml version="1.0" encoding="UTF-8"?>
<chunk version="1.2.0" label="Chunk 1" enabled="true">
  <sensors next_id="0"/>
  <cameras next_id="0" next_group_id="0"/>
  <frames next_id="1">
    <frame id="0" path="0/frame.zip"/>
  </frames>
  <reference>LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]</reference>
  <settings>
    <property name="accuracy_tiepoints" value="1"/>
    <property name="accuracy_cameras" value="10"/>
    <property name="accuracy_cameras_ypr" value="10"/>
    <property name="accuracy_markers" value="0.005"/>
    <property name="accuracy_scalebars" value="0.001"/>
    <property name="accuracy_projections" value="0.1"/>
  </settings>
</chunk>
        """
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())

    def generate_psx(self, index, doc_path):
        chunk_path = doc_path.joinpath(f"{index}")
        print(f" create {chunk_path}")
        if not chunk_path.is_dir():
            # create the chunk directory and the files in it.
            # a chunk.zip with a doc.xml inside it
            # and a frame? directory
            chunk_path.mkdir()

        for j, frame in enumerate(self.frames):
            frame.generate_psx(j, chunk_path)

        generate_zip(self, chunk_path, "chunk.zip")


@dataclass_json
@dataclass
class Document:
    name: str = ""
    version: str = ""
    path: str = ""

    next_id: int = None
    active_id: int = None

    chunks: List[Chunk] = field(default_factory=list)
    meta: List[Property] = field(default_factory=list)

    def defaults(self):
        self.meta.append(Property( name="Info/OriginalSoftwareName", value="pypsxlib"))
        self.meta.append(Property( name="Info/OriginalSoftwareVendor", value="Luke Miller"))
        self.meta.append(Property( name="Info/OriginalSoftwareVersion", value=__version__))

    def load_psx(self, fname):
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError
        document = None
        with ZipFile(fpath, 'r') as zf:
            for docfname in zf.filelist:
                xmlstr = zf.read(docfname)
                # convert the xml string into xml tree, take the document node and convert to json string, load to dataclass
                bf = dumps(gdata.data(fromstring(xmlstr))["document"])
                j = json.loads(bf)
                document = Document(version=j["version"], next_id=j["chunks"]["next_id"], active_id=j["chunks"]["active_id"])
                for key in j["chunks"].keys():
                    if key == "chunk":
                        chunk_json = j["chunks"][key]
                        cname = Path(fpath.parent, chunk_json["path"])
                        document.chunks.append(Chunk().load_psx(cname))
        return document

    def xml(self):
        root = etree.Element("document", version=__version_psx__)
        chunks = etree.Element("chunks", next_id=f"{len(self.chunks)}", active_id="0")
        for i, chunk in enumerate(self.chunks):
            chunk_xml = etree.Element("chunk", id=f"{i}", path=f"{i}/chunk.zip")
            chunks.append(chunk_xml)
        root.append(chunks)
        meta = etree.Element("meta")

        for property in self.meta:
            meta.append(etree.Element("property", name=property.name, value=property.value))

        """
        meta.append(etree.Element("property", name="Info/OriginalSoftwareName", value="pypsxlib"))
        meta.append(etree.Element("property", name="Info/OriginalSoftwareVendor", value="Luke Miller"))
        meta.append(etree.Element("property", name="Info/OriginalSoftwareVersion", value=__version__))
        """
        root.append(meta)
        """
<?xml version="1.0" encoding="UTF-8"?>
<document version="1.2.0">
  <chunks next_id="1" active_id="0">
    <chunk id="0" path="0/chunk.zip"/>
  </chunks>
  <meta>
    <property name="Info/OriginalSoftwareName" value="Agisoft Metashape"/>
    <property name="Info/OriginalSoftwareVendor" value="Agisoft"/>
    <property name="Info/OriginalSoftwareVersion" value="1.5.2.7838"/>
  </meta>
</document>
        
        """
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, xmlpath):
        with open(xmlpath, "wb") as f:
            f.write(self.xml())


@dataclass_json
@dataclass
class App:
    documents: List[Document] = field(default_factory=list)


@dataclass_json
@dataclass
class Project:
    name: str = None
    path: str = None
    apps: List[App] = field(default_factory=list)

    def defaults(self, chunk=True):
        """
        Create an empty project with one chunk
        """
        self.apps.append(App())
        document = Document()
        self.apps[0].documents.append(document)
        document.defaults()
        if chunk:
            self.add_chunk()

    def add_chunk(self):
        if not self.apps or not self.apps[0].documents:
            self.defaults()
        else:
            chunk = Chunk()
            chunk.defaults()
            self.apps[0].documents[0].chunks.append(chunk)
            self.apps[0].documents[0].chunks[-1].frames.append(Frame())
            self.apps[0].documents[0].chunks[-1].frames[0].thumbnails = Thumbnails()
        return self.apps[0].documents[0].chunks[-1]

    def load_psx(self, fname):
        fpath = Path(fname)
        self.name = fpath.stem
        if not fpath.is_file():
            raise FileNotFoundError

        with open(fname, "r") as f:
            xmlstr = f.read()
        # convert the xml string into xml tree, take the document node and convert to json string, load to dataclass
        bf = dumps(gdata.data(fromstring(xmlstr))["document"])
        document = Document.from_json(bf, infer_missing=True)
        if not self.apps:
            self.apps.append(App())
        dname = document.path.replace("{projectname}", self.name)
        dname = Path(fpath.parent, dname)
        document = Document().load_psx(dname)
        self.apps[-1].documents.append(document)
        return self

    def xml(self):
        root = etree.Element("document", version=__version_psx__, path="{projectname}.files/project.zip")
        return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def save(self, path=None, override=False):
        self.path = path if path else self.path
        project_path = Path(self.path)
        path = Path(self.path, self.name)
        files_path = path.with_suffix(".files")
        for p in [project_path, path, files_path]:
            if not p.is_dir():
                p.mkdir()
            elif not override:
                raise IsADirectoryError(f"directory {p} already exists")

        # go into files_path and create a directory per chunk and a high level project.zip contain doc.xml
        project_file = files_path.joinpath("project.zip")
        with ZipFile(project_file, 'w') as myzip:
            for app in self.apps:
                for doc in app.documents:
                    doc_file = files_path.joinpath("doc.xml")
                    doc.save(doc_file)
                    for i, chunk in enumerate(doc.chunks):
                        chunk.generate_psx(i, files_path)

                    myzip.write(doc_file, arcname="doc.xml")
                    doc_file.unlink()

        # create top level psx file
        psx_file = path.with_suffix(".psx")
        print(psx_file)
        with open(psx_file, "wb") as f:
            f.write(self.xml())


"""
<?xml version="1.0" encoding="UTF-8"?>
<document version="1.2.0" path="{projectname}.files/project.zip"/>
"""


def parse_xml(cwd, root, project_name):
    warnings.warn("`parse_xml` is a provisional function and may not exist in future versions.")
    # print out a psx project (call from parse_xmlfile)
    depth = " "*len(Path(cwd).parts)
    if root.text:
        print(depth, root.tag, root.attrib, root.text)
    else:
        print(depth, root.tag, root.attrib)

    if "path" in root.attrib:
        fname = root.attrib["path"]
        fname = fname.replace("{projectname}", project_name)
        fpath = Path(cwd, fname)
        if fpath.suffix == ".zip":
            print(depth,"z--", fpath.name)
            with ZipFile(fpath, 'r') as zf:
                for chunkfname in zf.filelist:
                    chunkfpath = Path(chunkfname.filename)
                    if chunkfpath.suffix == ".xml":
                        xmlstr = zf.read(chunkfname)
                        print(depth,"--z", chunkfpath.name)
                        cwd = Path(cwd).joinpath(fpath.parent)
                        xml = ET.fromstring(xmlstr)
                        #xmlprettyprint(xml)
                        parse_xml(cwd, xml, project_name)
                    else:
                        print(depth, "FILE IN ZIP",chunkfpath)
                        print()
        else:
            print(depth, "FILE", fpath)
            print()

    for child in root:
        parse_xml(cwd, child, project_name)


def parse_xmlfile(cwd, fname=None, project_name=None):
    warnings.warn("`parse_xmlfile` is a provisional function and may not exist in future versions.")

    # print out a psx project
    import xml.etree.ElementTree as ET
    if not fname:
        project_name = Path(cwd).stem
        fname = cwd
        cwd = Path(cwd).parent.as_posix()
    print("---",Path(fname).name)
    tree = ET.parse(fname)
    root = tree.getroot()
    parse_xml(cwd, root, project_name)


if __name__ == "__main__":
    pass
