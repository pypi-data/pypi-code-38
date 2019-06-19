import json
import os
import re

from requests import Response
from vedavaapi.client import VedavaapiSession


def post_graph(
        vc, graph, ool_data_graph=None,
        files=None, response_projection_map=None,
        should_return_resources=True, should_return_oold_resources=True,
        upsert=False):

    post_data = {
        "graph": json.dumps(graph),
        "ool_data_graph": json.dumps(ool_data_graph or {}),
        #  "files": files,
        "response_projection_map": json.dumps(response_projection_map or {"*": {"permissions": 0}}),
        "should_return_resources": json.dumps(should_return_resources),
        "should_return_oold_resources": json.dumps(should_return_oold_resources),
        "upsert": json.dumps(upsert)
    }

    for k in list(post_data.keys()):
        if post_data[k] is None:
            post_data.pop(k)

    post_files = [
        ("files", open(file, 'rb') if isinstance(file, str) else file)
        for file in files or []
    ]

    #  print(post_files)

    post_response = vc.post('objstore/v1/graph', data=post_data, files=post_files)  # type: Response
    if post_response.status_code != 200:
        print(post_response.json())
    post_response.raise_for_status()
    return post_response.json()


def get_graph(
        vc: VedavaapiSession, start_nodes_selector, traverse_key_filter_maps_list,
        start_nodes_sort_doc=None, start_nodes_offset=None, start_nodes_count=None,
        hop_inclusions_config=None, include_incomplete_paths=False,
        direction='referrer', max_hops=0, json_class_projection_map=None):

    get_params = {
        "start_nodes_selector": json.dumps(start_nodes_selector),
        "start_nodes_sort_doc": json.dumps(start_nodes_sort_doc) if start_nodes_sort_doc else None,
        "start_nodes_offset": start_nodes_offset,
        "start_nodes_count": start_nodes_count,

        "traverse_key_filter_maps_list": json.dumps(traverse_key_filter_maps_list),
        "direction": direction,
        "max_hops": max_hops,

        "hop_inclusions_config": json.dumps(hop_inclusions_config) if hop_inclusions_config else None,
        "include_incomplete_paths": json.dumps(include_incomplete_paths),

        "json_class_projection_map": json.dumps(json_class_projection_map) if json_class_projection_map else None
    }

    for k in list(get_params.keys()):
        if get_params[k] is None:
            get_params.pop(k)

    # print(get_params)
    get_response = vc.put('objstore/v1/graph', data=get_params)
    get_response.raise_for_status()
    return get_response.json()


def get_resources(vc: VedavaapiSession, selector_doc, projection=None, start=None, count=None, sort_doc=None):
    get_params = {
        "selector_doc": json.dumps(selector_doc),
        "projection": json.dumps(projection) if projection else None,
        "start": start,
        "count": count,
        "sort_doc": json.dumps(sort_doc) if sort_doc else None
    }

    for k in list(get_params.keys()):
        if get_params[k] is None:
            get_params.pop(k)

    get_response = vc.get('objstore/v1/resources', parms=get_params)
    get_response.raise_for_status()
    return get_response.json()


def get_children(
        vc: VedavaapiSession, resource_id, filter_doc=None,
        sort_doc=None, start=None, count=None, projection=None):
    selector_doc = filter_doc.copy()
    selector_doc.update({
        "source": resource_id
    })
    return get_resources(vc, selector_doc, projection=projection, start=start, count=count, sort_doc=sort_doc)


def get_annos(
        vc: VedavaapiSession, resource_id, filter_doc=None,
        sort_doc=None, start=None, count=None, projection=None):
    selector_doc = filter_doc.copy()
    selector_doc.update({
        "target": resource_id
    })
    return get_resources(vc, selector_doc, projection=projection, start=start, count=count, sort_doc=sort_doc)


def add_to_agent_ids(vc, resource_id, actions, control, to_be_added_user_ids=None, to_be_added_team_ids=None):
    """
    add users/teams to granted/withdrawn/blocked agents_set for selected 'actions' over the 'resource' with given resource_id
    see swagger_ui, for doc.

    """
    post_data = {
        "actions": json.dumps(actions),
        "control": control,
        "user_ids": json.dumps(to_be_added_user_ids or []),
        "team_ids": json.dumps(to_be_added_team_ids or [])
    }

    response = vc.post('acls/v1/{}'.format(resource_id), data=post_data)
    response.raise_for_status()
    return response.json()


def get_resolved_permissions(vc: VedavaapiSession, resource_id, actions=None):
    # for current_user, gives resolved permission details for given actions over resource

    get_params = {
        "actions": json.dumps(actions) if actions else None
    }

    for k in list(get_params.keys()):
        if get_params[k] is None:
            get_params.pop(k)

    response = vc.get('objstore/v1/resources/{}/resolved_permissions'.format(resource_id), parms=get_params)
    response.raise_for_status()

    return response.json()


def remove_nones_in_doc(doc):
    for k in list(doc.keys()):
        if doc[k] is None:
            doc.pop(k)


def import_book(
        vc, library_id, book_title, book_author_name,
        book_cover_image_file_path, page_images_file_paths,
        book_lang=None, book_script=None, book_genre=None,
        page_index_computing_fn=None, page_material=None, upsert=False):

    graph = {}
    ool_data_graph = {}

    files_paths = []

    # 1. create_book
    book_blank_id = '_:book1'
    book_title_jo = {"jsonClass": "Text", "chars": book_title}
    book_author_jo = {"jsonClass": "Person", "name": [{"jsonClass": "Text", "chars": book_author_name}]}

    lang_metadata_item = {"jsonClass": "MetadataItem", "label": "language", "value": book_lang} if book_lang else None
    book_genre_metadata_item = {"jsonClass": "MetadataItem", "label": "genre", "value": book_genre} if book_genre else None

    # book_cover_file's out of line dta's definition
    book_cover_file_name = book_cover_image_file_path.split('/')[-1]
    book_cover_ool_data_blank_id = '_:cover_page'
    book_cover_ool_data = {
        "jsonClass": "StillImage",
        "namespace": "_vedavaapi",
        "identifier": book_cover_file_name,
        "_id": book_cover_ool_data_blank_id,
        "source": '_VV:{}'.format(book_blank_id)
    }
    ool_data_graph[book_cover_ool_data_blank_id] = book_cover_ool_data
    files_paths.append(book_cover_image_file_path)

    # cover's stillImage representation, data being setted to abobve ool_data's blank_id
    book_cover_representation = {
        "jsonClass": "StillImageRepresentation",
        "data": '_OOLD:{}'.format(book_cover_ool_data_blank_id),
        "material": page_material,
        "implements": ["iiif_image"]
    }
    remove_nones_in_doc(book_cover_representation)

    book_metadata = []
    if lang_metadata_item is not None:
        book_metadata.append(lang_metadata_item)
    if book_genre_metadata_item is not None:
        book_metadata.append(book_genre_metadata_item)

    # book's definition
    book = {
        "jsonClass": "BookPortion",
        "_id": book_blank_id,
        "source": library_id,
        "metadata": book_metadata,
        "title": [book_title_jo],
        "author": [book_author_jo],
        "cover": book_cover_representation
    }
    #  print(book.to_json_map())
    graph[book_blank_id] = book

    # now pages
    page_member_infos = []
    for i, page_image_path in enumerate(page_images_file_paths):
        if page_index_computing_fn:
            page_index = page_index_computing_fn(page_image_path)
            page_selector = {"jsonClass": "IndexSelector", "index": page_index}
        else:
            page_index = None
            page_selector = {"jsonClass": "QualitativeSelector"}

        page_blank_id = '_:page_{}'.format(i)

        # page representations

        # page image out of line data.
        page_image_file_name = page_image_path.split('/')[-1]
        page_image_ool_data_blank_id = '_:page_image_{}'.format(i)
        page_image_ool_data = {
            "jsonClass": "StillImage",
            "namespace": "_vedavaapi",
            "identifier": page_image_file_name,
            "source": '_VV:{}'.format(page_blank_id)
        }

        ool_data_graph[page_image_ool_data_blank_id] = page_image_ool_data
        files_paths.append(page_image_path)

        # iumage representation of page, with data setted to above ool_data's blank_id
        page_image_repr = {
            "jsonClass": "StillImageRepresentation",
            "data": '_OOLD:{}'.format(page_image_ool_data_blank_id),
            "material": page_material,
            "script": book_script
        }
        remove_nones_in_doc(page_image_repr)

        # all page representations. presently only containing stillImage representation.
        page_representations = {
            "jsonClass": "DataRepresentations",
            "stillImage": [page_image_repr],
            "default": "stillImage"
        }

        # page's definition
        page = {
            "jsonClass": "Page",
            "source": book_blank_id,
            "selector": page_selector,
            "representations": page_representations
        }
        graph[page_blank_id] = page

        # for sequence annotation
        page_member_info = {
            "jsonClass": "WrappreObject",
            "index": page_index,
            "resource": page_blank_id
        }
        page_member_infos.append(page_member_info)

    response = post_graph(
        vc, graph, ool_data_graph=ool_data_graph,
        files=files_paths, response_projection_map={"*": {"permissions": 0}},
        should_return_resources=True, should_return_oold_resources=True,
        upsert=upsert
    )

    # now creating default sequence annotation over book
    sequence_anno = create_default_page_sequence_annotation(book_blank_id, response['graph'], page_member_infos)
    sequence_anno_response = post_graph(
        vc, {"_:seqanno": sequence_anno},
        response_projection_map={"*": {"permissions": 0}},
        should_return_resources=True, upsert=upsert
    )

    return book_blank_id, response['graph'][book_blank_id]['_id'], response, sequence_anno_response


def create_default_page_sequence_annotation(book_blank_id, graph, members, index_props=None):
    book_id = graph[book_blank_id]['_id'] if isinstance(graph[book_blank_id], dict) else graph[book_blank_id]
    sequence_members = []
    explicit_indices = bool(
        members and len(members) and members[0]
        and 'index' in members[0] and members[0]['index']
    )
    for i, member in enumerate(members):
        index = member['index'] if explicit_indices else str(i)
        member_blank_id = member['resource']
        sequence_member_id = graph[member_blank_id]['_id'] if isinstance(graph[member_blank_id], dict) else graph[member_blank_id]
        sequence_member = {
            "jsonClass": "WrapperObject",
            "index": index,
            "resource": sequence_member_id
        }
        sequence_members.append(sequence_member)

    if index_props is None:
        index_props = {
            "jsonClass": "WrapperObject",
            "indexPartsRegex": r"^(?P<page_no>.*)$",
            "allNumeral": True,
            "indexPartsMaxLength": [5],
            "padChar": "0"
        }

    body = {
        "jsonClass": "WrapperObject",
        "members": sequence_members,
        "sequenceType": "page_sequence",
        "indexProperties": index_props
    }
    sequence_anno = {
        "jsonClass": "SequenceAnnotation",
        "target": book_id,
        "body": body,
        "canonical": 'default_canvas_sequence'
    }
    return sequence_anno


def import_book_from_dir(
        vc, library_id, book_title, book_author_name,
        book_cover_image_file_path, page_images_directory,
        book_lang=None, book_script=None, book_genre=None,
        page_index_regex=None, page_material=None, upsert=False):

    page_image_file_names = sorted(os.listdir(page_images_directory))
    page_image_file_paths = [os.path.join(page_images_directory, fn) for fn in page_image_file_names]

    def page_index_computing_fn(page_file_path):
        file_name = page_file_path.split('/')[-1]
        return re.match(page_index_regex, file_name).group('index')

    return import_book(
        vc, library_id, book_title, book_author_name,
        book_cover_image_file_path, page_image_file_paths,
        book_lang=book_lang, book_script=book_script, book_genre=book_genre,
        page_index_computing_fn=page_index_computing_fn if page_index_regex else None,
        page_material=page_material, upsert=upsert
    )
