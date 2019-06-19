import os
import re

import requests

from . import objstore
from .objstore import create_default_page_sequence_annotation


def remove_nones_from_doc(doc):
    for key in list(doc.keys()):
        if doc[key] is None:
            doc.pop(key)
    return doc

# interface for id adapting
class IdAdapter(object):

    def normalize_to_manifest_uri(self, book_url):
        return book_url

    def book_id_match(self, manifest_iri):
        pass

    def get_manifest_iri(self, book_id):
        pass

    def page_id_match(self, canvas_iri):
        pass

    def get_canvas_iri(self, book_id, page_id):
        pass

    def get_image_json_iri(self, image_id):
        pass


# ool data representation adapter
class OOLDataRepresentationAdapter(object):

    should_resolve_throgh_info_json = False

    def book_ool_data(self, manifest, source_id):
        pass

    def book_representation(self, manifest, ool_data, **kwargs):
        pass

    def book_thumbnail_url(self, manifest):
        pass

    def page_ool_data(self, canvas, source_id, **kwargs):
        pass

    def page_representation(self, canvas, ool_data, **kwargs):
        pass


class InteractiveDataRepresentationAdapter(OOLDataRepresentationAdapter):
    pass


class StillImageRepresentationAdapter(OOLDataRepresentationAdapter):
    pass


class SimpleIIIFIdAdapter(IdAdapter):

    manifest_iri_re = re.compile(r'^(?P<book_id>.+)$')
    # noinspection RegExpRedundantEscape
    canvas_iri_re = re.compile(r'^(?P<page_id>.+)$')


    def book_id_match(self, manifest_iri):
        return self.manifest_iri_re.match(manifest_iri)

    def get_manifest_iri(self, book_id):
        return book_id

    def page_id_match(self, canvas_iri):
        return self.canvas_iri_re.match(canvas_iri)

    def get_canvas_iri(self, book_id, page_id):
        return page_id

    def get_image_json_iri(self, image_id):
        return image_id


class SimpleStillImageReprAdapter(StillImageRepresentationAdapter):

    def __init__(self, id_adapter, namespace):
        self.id_adapter = id_adapter
        self.namespace = namespace

    def book_thumbnail_url(self, manifest):
        manifest.get('thumbnail', {}).get('@id', None)

    def page_ool_data(self, canvas, source_id, **kwargs):

        def set_default_json_class(doc):
            if isinstance(doc, dict):
                doc['jsonClass'] = 'WrapperObject'
                for k, v in doc.items():
                    set_default_json_class(v)
            if isinstance(doc, list):
                for item in doc:
                    set_default_json_class(item)

        iiif_image_resources = [image['resource'] for image in canvas['images']]
        set_default_json_class(iiif_image_resources)
        iiif_image_resource = iiif_image_resources[0]

        namespace_data = {
            "jsonClass": "OOLDNamespaceData",
            "namespace": self.namespace,
            "canvas_url": canvas['@id'],
            "iiif_image": iiif_image_resource
        }

        ool_data = {
            "jsonClass": "StillImage",
            "namespace": self.namespace,
            "identifier": canvas['@id'],
            "namespaceData": namespace_data,
            "url": os.path.join(iiif_image_resource['service']['@id'], 'full/full/0/default.jpg'),
            "source": source_id
        }
        return ool_data

    def page_representation(self, canvas, ool_data, material=None, script=None, **kwargs):
        page_repr = {
            "jsonClass": "StillImageRepresentation",
            "data": '_OOLD:{}'.format(ool_data['_id']),
            "implements": ["iiif_image"],
            "height": ool_data['namespaceData']['iiif_image']['height'],
            "width": ool_data['namespaceData']['iiif_image']['width'],
        }
        return page_repr


def book_graph_from_manifest(
        library_id, manifest, book_title, authors_names,
        book_material, book_script,
        id_adapter, interactive_repr_adapter, still_image_repr_adapter):

    book = {
        "jsonClass": "ScannedBook"
    }
    ool_data_graph = {}

    manifest_metadata = manifest.get('metadata', [])[:]

    book_id = id_adapter.book_id_match(manifest['@id']).group('book_id')
    book_blank_id = '_:book_{}'.format(book_id)

    if authors_names and len(authors_names):
        authors = [author for author in authors_names if not re.match(r'^\s+$', author)]
    else:
        authors = None

    thumbnail_url = still_image_repr_adapter.book_thumbnail_url(manifest)
    if thumbnail_url:
        thumbnail_oold_blank_id = '_:book_{}_thumbnail_img'.format(book_id)
        thumbnail_ool_data = {
            "jsonClass": "StillImage",
            "namespace": "_web",
            "identifier": thumbnail_url,
            "url": thumbnail_url,
            "source": '_VV:{}'.format(book_blank_id)
        }
        ool_data_graph[thumbnail_oold_blank_id] = thumbnail_ool_data

        thumbnail_representation = {
            "jsonClass": "StillImageRepresentation",
            "data": '_OOLD:{}'.format(thumbnail_oold_blank_id),
        }

        book['cover'] = thumbnail_representation

    book_reprs = {
        "jsonClass": "DataRepresentations"
    }

    still_image_oold = still_image_repr_adapter.book_ool_data(manifest, '_VV:{}'.format(book_blank_id))
    if still_image_oold:
        still_image_oold_blank_id = '_:book_{}_pdf'.format(book_id)
        still_image_oold['_id'] = still_image_oold_blank_id
        ool_data_graph[still_image_oold_blank_id] = still_image_oold

        still_image_repr = still_image_repr_adapter.book_representation(
            manifest, still_image_oold, material=book_material, script=book_script
        )
        manifest_metadata.append({"label": "related", "value": still_image_oold['url']})
        book_reprs['stillImage'] = [still_image_repr]

    interactive_oold = interactive_repr_adapter.book_ool_data(manifest, "_VV:{}".format(book_blank_id))
    if interactive_oold:
        interactive_oold_blank_id = '_:book_{}_book_reader'.format(book_id)
        interactive_oold['_id'] = interactive_oold_blank_id
        ool_data_graph[interactive_oold_blank_id] = interactive_oold

        interactive_repr = interactive_repr_adapter.book_representation(
            manifest, interactive_oold
        )
        manifest_metadata.append({"label": "related", "value": interactive_oold['url']})
        book_reprs['interactiveResource'] = [interactive_repr]

    if 'stillImage' in book_reprs:
        book_reprs['default'] = 'stillImage'
    elif 'interactiveResource' in book_reprs:
        book_reprs['default'] = 'interactiveResource'
    else:
        book_reprs = None

    book.update({
        "source": library_id,
        "title": book_title,
        "author": authors,
        "metadata": [{"jsonClass": "MetadataItem", "label": m['label'], "value": m['value']} for m in manifest_metadata],
        "representations": book_reprs,
    })
    remove_nones_from_doc(book)

    return {book_blank_id: book}, ool_data_graph, book_blank_id


def pages_graph_from_canvas(
        library_id, book_blank_id, canvas,
        book_material, book_script,
        id_adapter, interactive_repr_adapter, still_image_repr_adapter, page_id_info_jsons_map=None):

    ool_data_graph = {}

    page = {
        "jsonClass": "ScannedPage"
    }
    canvas_iri_parts_match = id_adapter.page_id_match(canvas['@id'])
    canvas_id_parts_dict = canvas_iri_parts_match.groupdict()
    page_id = canvas_id_parts_dict.get('page_id')
    page_index = canvas_id_parts_dict.get('page_index', None)
    page_blank_id = '_:page_{}'.format(page_id)

    page_reprs = {
        "jsonClass": "DataRepresentations"
    }

    still_image_oold_blank_id = '_:page_{}_iiif'.format(page_id)
    info_json = (page_id_info_jsons_map or {}).get(page_id, None)
    still_image_oold = still_image_repr_adapter.page_ool_data(canvas, '_VV:{}'.format(page_blank_id), info_json=info_json)
    still_image_oold['_id'] = still_image_oold_blank_id
    ool_data_graph[still_image_oold_blank_id] = still_image_oold

    still_image_repr = still_image_repr_adapter.page_representation(
        canvas, still_image_oold, material=book_material, script=book_script
    )
    page_reprs.update({
        "stillImage": [still_image_repr],
        "default": "stillImage"
    })

    interactive_oold = interactive_repr_adapter.page_ool_data(canvas, '_VV:{}'.format(page_blank_id))
    if interactive_oold:
        interactive_oold_blank_id = '_:page_{}_book_reader'.format(page_id)
        interactive_oold['_id'] = interactive_oold_blank_id
        ool_data_graph[interactive_oold_blank_id] = interactive_oold

        interactive_repr = interactive_repr_adapter.page_representation(
            canvas, interactive_oold
        )
        page_reprs.update({
            "interactiveResource": [interactive_repr]
        })

    page.update({"source": book_blank_id, "representations": page_reprs})

    if page_index:
        selector = {
            "jsonClass": "IndexSelector",
            "index": page_index
        }
    else:
        selector = {
            "jsonClass": "QualitativeSelector"
        }
    page['selector'] = selector

    return {page_blank_id: page}, ool_data_graph, page_blank_id, page_id, page_index


def marshal_manifest_to_book_graph(
        library_id, manifest, metadata_keys_map,
        book_material, book_script,
        id_adapter, interactive_repr_adapter, still_image_repr_adapter,
        book_title=None, language=None, authors_names=None, update_state=None):

    graph = {}
    ool_data_graph = {}

    title = book_title or manifest['label']

    manifest_metadata = manifest.get('metadata', [])
    manifest_metadata_map = dict((mi['label'], mi['value']) for mi in manifest_metadata)

    if not authors_names and 'author' in metadata_keys_map:
        manifest_metadata_author_key = metadata_keys_map['author']
        authors_names = manifest_metadata_map.get(manifest_metadata_author_key, None)
        if isinstance(authors_names, str):
            authors_names = authors_names.strip().lstrip(',').rstrip(',').split(',')
    if not language and 'language' in metadata_keys_map:
        manifest_metadata_lang_key = metadata_keys_map['language']
        language = manifest_metadata_map.get(manifest_metadata_lang_key, None)

    book_graph, book_ool_data_graph, book_blank_id = book_graph_from_manifest(
        library_id, manifest, title, authors_names,
        book_material, book_script,
        id_adapter, interactive_repr_adapter, still_image_repr_adapter
    )

    graph.update(book_graph)
    ool_data_graph.update(book_ool_data_graph)

    default_sequence = manifest['sequences'][0]
    canvases = default_sequence['canvases']
    if update_state:
        update_state(state='PROGRESS', meta={"total_pages": len(canvases), "resolved_pages": 0})
    if still_image_repr_adapter.should_resolve_throgh_info_json:
        page_id_info_jsons_map = still_image_repr_adapter.get_infos(canvases, update_state=update_state)
    else:
        page_id_info_jsons_map = {}
    page_members = []
    for canvas in canvases:
        page_graph, page_ool_data_graph, page_blank_id, page_id, page_index = pages_graph_from_canvas(
            library_id, book_blank_id, canvas,
            book_material, book_script,
            id_adapter, interactive_repr_adapter, still_image_repr_adapter, page_id_info_jsons_map=page_id_info_jsons_map
        )
        graph.update(page_graph)
        ool_data_graph.update(page_ool_data_graph)

        page_member = {
            "index": page_index,
            "resource": page_blank_id
        }
        page_members.append(page_member)

    return graph, ool_data_graph, book_blank_id, page_members


class ArchiveIdAdapter(SimpleIIIFIdAdapter):

    manifest_iri_re = re.compile(r'https://iiif.archivelab.org/iiif/(?P<book_id>[^/]+)/manifest\.json')
    # noinspection RegExpRedundantEscape
    canvas_iri_re = re.compile(
        r'https://iiif.archivelab.org/iiif/(?P<page_id>(?P<book_id>[^/\$]+)\$?(?P<page_index>[^/]+))?/canvas'
    )

    manifest_iri_format_string = 'https://iiif.archivelab.org/iiif/{object_id}/manifest.json'

    canvas_iri_format_string = 'https://iiif.archivelab.org/iiif/{object_id}${canvas_id}/canvas'

    image_json_iri_format_string = 'https://iiif.archivelab.org/iiif/{image_id}/info.json'

    def normalize_to_manifest_uri(self, book_url):
        if book_url.startswith('https://archive'):
            # noinspection RegExpRedundantEscape
            match_obj = re.match(r'https://archive.org/[^/]+/(?P<book_id>[^/\$#]+).*$', book_url)
            book_id = match_obj.group('book_id')
            return 'https://iiif.archivelab.org/iiif/{}/manifest.json'.format(book_id)
        else:
            match_obj = self.book_id_match(book_url)
            if not match_obj:
                raise ValueError('given url is not valid archive.org book/manifest url')
            return book_url

    def get_image_json_iri(self, image_id):
        return self.image_json_iri_format_string.format(image_id=image_id)


class ArchiveInteractiveReprAdapter(InteractiveDataRepresentationAdapter):

    def __init__(self):
        self.id_adapter = ArchiveIdAdapter()
        self.namespace = 'archive.org'

    def book_ool_data(self, manifest, source_id):
        manifest_iri_parts_match = self.id_adapter.book_id_match(manifest['@id'])
        book_id = manifest_iri_parts_match.group('book_id')

        archive_book_link = 'https://archive.org/stream/{}'.format(book_id)
        namespace_data = {
            "jsonClass": "OOLDNamespaceData",
            "namespace": self.namespace,
            "href": archive_book_link,
            "type": "item"
        }
        ool_data = {
            "jsonClass": "InteractiveResource",
            "namespace": self.namespace,
            "identifier": book_id,
            "namespaceData": namespace_data,
            "url": archive_book_link,
            "source": source_id
        }
        return ool_data

    def book_representation(self, manifest, ool_data, **kwargs):
        book_repr = {
            "jsonClass": "DataRepresentation",
            "data": '_OOLD:{}'.format(ool_data['_id']),
            "interaction_type": "archive_book_reader"
        }
        return book_repr

    def page_ool_data(self, canvas, source_id, **kwargs):
        canvas_iri_parts_match = self.id_adapter.page_id_match(canvas['@id'])
        page_id = canvas_iri_parts_match.group('page_id')
        book_id = canvas_iri_parts_match.group('book_id')
        page_index = canvas_iri_parts_match.group('page_index')

        archive_page_link = 'https://archive.org/stream/{}#page/n{}'.format(book_id, page_index)
        namespace_data = {
            "jsonClass": "OOLDNamespaceData",
            "namespace": self.namespace,
            "href": archive_page_link,
            "type": "leaf",
            "index": page_index,
            "book_id": book_id
        }

        ool_data = {
            "jsonClass": "InteractiveResource",
            "namespace": self.namespace,
            "identifier": page_id,
            "namespaceData": namespace_data,
            "url": archive_page_link,
            "source": source_id
        }
        return ool_data

    def page_representation(self, canvas, ool_data, **kwargs):
        page_repr = {
            "jsonClass": "DataRepresentation",
            "data": '_OOLD:{}'.format(ool_data['_id']),
            "interactionType": "archive_book_reader"
        }
        return page_repr


class ArchiveStillImageReprAdapter(SimpleStillImageReprAdapter):

    should_resolve_throgh_info_json = True

    def __init__(self, *args):
        id_adapter = ArchiveIdAdapter()
        namespace = 'archive.org'
        super(ArchiveStillImageReprAdapter, self).__init__(id_adapter, namespace)

    def book_ool_data(self, manifest, source_id):
        manifest_iri_parts_match = self.id_adapter.book_id_match(manifest['@id'])
        book_id = manifest_iri_parts_match.group('book_id')

        archive_book_pdf_link = 'https://archive.org/download/{}/{}.pdf'.format(book_id, book_id)
        namespace_data = {
            "jsonClass": "OOLDNamespaceData",
            "namespace": self.namespace,
            "href": archive_book_pdf_link,
            "mimetype": "application/pdf",
            "type": "item"
        }
        ool_data = {
            "jsonClass": "StillImage",
            "namespace": self.namespace,
            "identifier": book_id,
            "namespaceData": namespace_data,
            "url": archive_book_pdf_link,
            "source": source_id
        }
        return ool_data

    def book_representation(self, manifest, ool_data, material=None, script=None):
        book_repr = {
            "jsonClass": "StillImageRepresentation",
            "data": '_OOLD:{}'.format(ool_data['_id']),
            "mimetype": "application/pdf",
        }
        return book_repr

    def book_thumbnail_url(self, manifest):
        manifest_iri_parts_match = self.id_adapter.book_id_match(manifest['@id'])
        book_id = manifest_iri_parts_match.group('book_id')
        return 'https://archive.org/services/img/{}'.format(book_id)

    def get_infos(self, canvases, update_state=None):
        info_iris = []
        page_id_info_iris_map = {}
        #  print('id_adapter type: ', type(self.id_adapter))
        for canvas in canvases:
            canvas_iri_parts_match = self.id_adapter.page_id_match(canvas['@id'])
            page_id = canvas_iri_parts_match.group('page_id')
            image_info_json_iri = self.id_adapter.get_image_json_iri(page_id)
            #  print(page_id, image_info_json_iri)
            info_iris.append(image_info_json_iri)
            page_id_info_iris_map[page_id] = image_info_json_iri
        from .async_requests_helper import get_urls
        info_jsons = get_urls(info_iris, update_state=update_state)
        info_iri_jsons_map = dict((j['@id'] + '/info.json', j) for j in info_jsons if j is not None)
        # print(info_iri_jsons_map.keys(), '\n\n\n', page_id_info_iris_map.values())
        page_id_info_jsons_map = dict((page_id, info_iri_jsons_map.get(page_id_info_iris_map[page_id], None)) for page_id in page_id_info_iris_map)
        return page_id_info_jsons_map

    def page_ool_data(self, canvas, source_id, info_json=None, **kwargs):
        ool_data = super(ArchiveStillImageReprAdapter, self).page_ool_data(canvas, source_id)
        ool_data['namespaceData']['type'] = 'leaf'

        if info_json:
            ool_data['namespaceData']['iiif_image']['height'] = info_json['height']
            ool_data['namespaceData']['iiif_image']['width'] = info_json['width']
        return ool_data

'''
class IhgIdAdapter(SimpleIIIFIdAdapter):
    manifest_iri_re = re.compile(r'^.*/(?P<book_id>[^/]+)/manifest\.json$')
    # noinspection RegExpRedundantEscape
    canvas_iri_re = re.compile(r'^.*/(?P<book_id>[^/]+)/canvas/(?P<page_id>(?P<page_index>[^\./]+)\.?[^\./]*).json')

'''


class IIIFImporter(object):
    id_adapter_cls = SimpleIIIFIdAdapter
    still_image_repr_adapter_cls = SimpleStillImageReprAdapter
    interactive_repr_adapter_cls = InteractiveDataRepresentationAdapter
    metadata_keys_map = None

    _importer_registry = {}

    def __init__(self, update_state=None):
        self.id_adapter = self.id_adapter_cls()
        self.still_image_repr_adapter = self.still_image_repr_adapter_cls(self.id_adapter, '_iiif')
        self.interactive_repr_adapter = self.interactive_repr_adapter_cls()
        self.update_state = update_state

    @classmethod
    def get_importer(cls, namespace):
        importer_cls = cls._importer_registry.get(namespace, IIIFImporter)
        return importer_cls()

    @classmethod
    def register_importer(cls, namespace, importer_cls):
        cls._importer_registry[namespace] = importer_cls

    def graph_from_book_url(self, book_url, library_id, book_material=None, book_script=None):
        manifest_url = self.id_adapter.normalize_to_manifest_uri(book_url)
        manifest = requests.get(manifest_url).json()

        graph, ool_data_graph, book_blank_id, page_members = marshal_manifest_to_book_graph(
            library_id, manifest, self.metadata_keys_map or {"author": "creator"},
            book_material, book_script,
            self.id_adapter, self.interactive_repr_adapter, self.still_image_repr_adapter, update_state=self.update_state
        )
        return graph, ool_data_graph, book_blank_id, page_members

    def get_sequence_annotation(self, book_blank_id, graph, page_members, index_props=None):
        return create_default_page_sequence_annotation(book_blank_id, graph, page_members, index_props=index_props)

    def import_from_book_url(self, vc, book_url, library_id, book_material=None, book_script=None, upsert=False):
        graph, ool_data_graph, book_blank_id, page_members = self.graph_from_book_url(
            book_url, library_id, book_material=book_material, book_script=book_script
        )

        response = objstore.post_graph(
            vc, graph, ool_data_graph,
            should_return_resources=False, should_return_oold_resources=True,
            upsert=upsert
        )

        #  print(response)

        sequence_anno = self.get_sequence_annotation(book_blank_id, response['graph'], page_members)
        sequence_anno_response = objstore.post_graph(
            vc, {"_:seqanno": sequence_anno}, ool_data_graph={},
            should_return_resources=False, upsert=upsert
        )

        return {
            "book_id": response['graph'][book_blank_id],
            "sequence_anno_id": sequence_anno_response['graph']['_:seqanno'],
            "total_pages": len(page_members), "resolved_pages": len(page_members)
        }


class ArchiveImporter(IIIFImporter):
    id_adapter_cls = ArchiveIdAdapter
    still_image_repr_adapter_cls = ArchiveStillImageReprAdapter
    interactive_repr_adapter_cls = ArchiveInteractiveReprAdapter

IIIFImporter.register_importer('archive.org', ArchiveImporter)
