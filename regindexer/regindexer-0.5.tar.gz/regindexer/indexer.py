from regindexer.config import Config

import codecs
import base64
import hashlib
import logging
import json
import requests
import os
import sys
from six.moves.urllib.parse import urljoin

log = logging.getLogger('regindexer')


MEDIA_TYPE_MANIFEST_V2 = 'application/vnd.docker.distribution.manifest.v2+json'
MEDIA_TYPE_LIST_V2 = 'application/vnd.docker.distribution.manifest.list.v2+json'
MEDIA_TYPE_OCI = 'application/vnd.oci.image.manifest.v1+json'
MEDIA_TYPE_OCI_INDEX = 'application/vnd.oci.image.index.v1+json'

MANIFEST_HEADERS = {
    'Accept': ', '.join((
        MEDIA_TYPE_MANIFEST_V2,
        MEDIA_TYPE_LIST_V2,
        MEDIA_TYPE_OCI,
        MEDIA_TYPE_OCI_INDEX,
    ))
}

DATA_URI_PREFIX = 'data:image/png;base64,'


class DownloadInfo(object):
    def __init__(self, digest, content_type, json):
        self.digest = digest
        self.content_type = content_type
        self.json = json

    def __repr__(self):
        return 'DownloadInfo(%r)' % self.__dict__


class RegistryQuery(object):
    def __init__(self, registry, verbose=False):
        self.registry = registry
        self.verbose = verbose
        self.session = requests.Session()

    def _get(self, relative_url, headers=None):
        return self.session.get(self.registry + relative_url,
                                headers=headers)

    def get_manifest(self, name, ref):
        log.info("Querying %s:%s", name, ref)

        url = '/v2/{}/manifests/{}'.format(name, ref)
        response = self._get(url, headers=MANIFEST_HEADERS)
        if response.status_code != 200:
            log.warning("Could not download %s:%s", name, ref)
            return None

        return DownloadInfo(response.headers['Docker-Content-Digest'],
                            response.headers['Content-Type'],
                            response.json())

    def get_blob(self, name, digest):
        url = '/v2/{}/blobs/{}'.format(name, digest)
        response = self._get(url)
        if response.status_code != 200:
            return None

        return DownloadInfo(response.headers['Docker-Content-Digest'],
                            response.headers['Content-Type'],
                            response.json())

    def list_repos(self):
        CHUNK_SIZE = 1000

        relative_url = '/v2/_catalog?n={}'.format(CHUNK_SIZE)
        chunk = self._get(relative_url).json()['repositories']
        repo_names = chunk
        while len(chunk) == CHUNK_SIZE:
            relative_url = '/v2/_catalog?n={}&last={}'.format(CHUNK_SIZE, repo_names[-1])
            chunk = self._get(relative_url).json()['repositories']
            print(chunk)
            repo_names.extend(chunk)

        return repo_names

    def iterate_images(self, tag_patterns):
        for name in self.list_repos():
            url = '/v2/{}/tags/list'.format(name)
            tags = self._get(url).json()['tags']
            matches = set()

            for tag in tags:
                for pat in tag_patterns:
                    if pat.matches(tag):
                        matches.add(tag)

            manifests = {}
            tags = {}
            for tag in matches:
                manifest_info = self.get_manifest(name, tag)
                if not manifest_info:
                    continue

                manifests[manifest_info.digest] = manifest_info
                tags.setdefault(manifest_info.digest, []).append(tag)

            for digest in manifests:
                yield name, manifests[digest], tags[digest]


class IconStore(object):
    def __init__(self, icons_dir, icons_uri):
        self.icons_dir = icons_dir
        self.icons_uri = icons_uri

        if not os.path.exists(icons_dir):
            # Create only one level
            os.mkdir(icons_dir)

        self.old_icons = {}
        for subdir in os.listdir(icons_dir):
            for filename in os.listdir(os.path.join(icons_dir, subdir)):
                self.old_icons[(subdir, filename)] = True

        self.icons = {}

    def store(self, uri):
        if not uri.startswith(DATA_URI_PREFIX):
            return None

        decoded = base64.b64decode(uri[len(DATA_URI_PREFIX):])

        h = hashlib.sha256()
        h.update(decoded)
        digest = h.hexdigest()
        subdir = digest[:2]
        filename = digest[2:] + '.png'

        key = (subdir, filename)
        if key in self.icons:
            pass
        elif key in self.old_icons:
            self.icons[key] = True
        else:
            if not os.path.exists(os.path.join(self.icons_dir, subdir)):
                os.mkdir(os.path.join(self.icons_dir, subdir))
            fullpath = os.path.join(self.icons_dir, subdir, filename)
            log.info("Storing icon: %s", fullpath)
            with open(os.path.join(self.icons_dir, subdir, filename), 'wb') as f:
                f.write(decoded)
            self.icons[key] = True

        return urljoin(self.icons_uri, subdir + '/' + filename)

    def clean(self):
        for key in self.old_icons:
            if key not in self.icons:
                subdir, filename = key
                fullpath = os.path.join(self.icons_dir, subdir, filename)
                os.unlink(fullpath)
                log.info("Removing icon: %s", fullpath)


class Index(object):
    def __init__(self, conf, icon_store=None):
        if conf.extract_icons and icon_store is None:
            raise RuntimeError("extract_icons is set, but no icons_dir is configured")

        self.config = conf
        self.icon_store = icon_store
        self.repos = {}

    def extract_icon(self, annotations, key):
        if not self.config.extract_icons:
            return

        value = annotations.get(key)
        if value is None:
            return

        uri = self.icon_store.store(value)
        if uri is not None:
            annotations[key] = uri

    def make_image(self, query, name, manifest_info, tags=None):
        config_info = query.get_blob(name, manifest_info.json['config']['digest'])
        if not config_info:
            log.warning("Failed to download config json")
            return None

        arch = config_info.json['architecture']
        os = config_info.json['os']

        if self.config.architectures:
            if arch not in self.config.architectures:
                return None

        if manifest_info.content_type == MEDIA_TYPE_OCI:
            annotations = manifest_info.json['annotations']
        else:
            annotations = {}

        for annotation in self.config.required_annotations:
            if annotation not in annotations:
                return None

        self.extract_icon(annotations, 'org.freedesktop.appstream.icon-64')
        self.extract_icon(annotations, 'org.freedesktop.appstream.icon-128')

        image = {
            'Digest': manifest_info.digest,
            'MediaType': manifest_info.content_type,
            'OS': os,
            'Architecture':  arch,
            'Labels': {},
        }

        image['Annotations'] = annotations

        labels = config_info.json['config'].get('Labels')
        if labels is None:
            labels = {}
        image['Labels'] = labels

        if tags:
            image['Tags'] = tags

        return image

    def make_list(self, query, name, list_info, tags=None):
        images = []
        for manifest in list_info.json['manifests']:
            manifest_info = query.get_manifest(name, manifest['digest'])

            if not manifest_info:
                log.warning("Failed to download manifest {}".format(manifest['digest']),
                            file=sys.stderr)
                continue

            if manifest_info.content_type in (MEDIA_TYPE_OCI, MEDIA_TYPE_MANIFEST_V2):
                image = self.make_image(query, name, manifest_info)
                if image:
                    images.append(image)

        if len(images) == 0:
            return None

        image_list = {
            'Digest': list_info.digest,
            'MediaType': list_info.content_type,
            'Images': images,
        }

        if tags:
            image_list['Tags'] = tags

        return image_list

    def add_image_or_list(self, query, name, info, tags):
        if name not in self.repos:
            self.repos[name] = {
                "Name": name,
                "Images": [],
                "Lists": [],
            }

        repo = self.repos[name]

        if info.content_type in (MEDIA_TYPE_OCI,  MEDIA_TYPE_MANIFEST_V2):
            image = self.make_image(query, name, info, tags=tags)
            if image:
                repo["Images"].append(image)
        elif info.content_type in (MEDIA_TYPE_OCI_INDEX, MEDIA_TYPE_LIST_V2):
            image_list = self.make_list(query, name, info, tags=tags)
            if image_list:
                repo["Lists"].append(image_list)
        else:
            log.info("{}/{}: not an OCI image or image index".format(name, tags))

    def write(self):
        with open(self.config.output, 'wb') as f:
            filtered_repos = (v for v in self.repos.values() if v['Images'] or v['Lists'])
            sorted_repos = sorted(filtered_repos, key=lambda r: r['Name'])
            for repo in sorted_repos:
                repo["Images"].sort(key=lambda x: x["Tags"])
                repo["Lists"].sort(key=lambda x: x["Tags"])

            writer = codecs.getwriter("utf-8")(f)
            json.dump({
                'Registry': self.config.registry_public,
                'Results': sorted_repos,
            }, writer, sort_keys=True, indent=4, ensure_ascii=False)
            writer.close()
        log.info("Wrote %s", self.config.output)


class Indexer(object):
    def __init__(self, config):
        self.conf = Config(config)

    def index(self):
        if not self.conf.indexes:
            log.warning("No indexes configured")
            return

        icon_store = None
        if self.conf.icons_dir is not None:
            if self.conf.icons_uri is None:
                raise RuntimeError("icons_dir is configured, but not icons_uri")

            icon_store = IconStore(self.conf.icons_dir, self.conf.icons_uri)

        indexes_by_registry = {}
        for index_config in self.conf.indexes:
            indexes = indexes_by_registry.setdefault(index_config.registry, [])
            indexes.append(Index(index_config, icon_store=icon_store))

        for registry, indexes in indexes_by_registry.items():
            query = RegistryQuery(registry)

            tag_patterns = set()
            for index in indexes:
                tag_patterns.update(index.config.tags)

            for repo, image, tags in query.iterate_images(tag_patterns):
                for index in indexes:
                    matches_tag = False
                    for tag in tags:
                        for tag_pattern in index.config.tags:
                            if tag_pattern.matches(tag):
                                matches_tag = True
                    if matches_tag:
                        index.add_image_or_list(query, repo, image, tags)

            for index in indexes:
                index.write()

        if icon_store is not None:
            icon_store.clean()
