# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT License, included in this distribution as LICENSE

"""
"""
import os

from metapack import MetapackPackageUrl, MetapackUrl, open_package
from metapack.cli.core import find_packages, prt, write_doc
from metatab import DEFAULT_METATAB_FILE
from rowgenerators import parse_app_url

from .package import (CsvPackageBuilder, ExcelPackageBuilder,
                      FileSystemPackageBuilder, ZipPackageBuilder)


def _exec_build(p, package_root, force, nv_name, extant_url_f, post_f):
    from metapack import MetapackUrl

    if force:
        reason = 'Forcing build'
        should_build = True
    elif p.is_older_than_metadata():
        reason = 'Metadata is younger than package'
        should_build = True
    elif not p.exists():
        reason = "Package doesn't exist"
        should_build = True
    else:
        reason = 'Metadata is older than package'
        should_build = False

    if should_build:
        prt("Building {} package ({})".format(p.type_code, reason))
        url = p.save()
        prt("Package ( type: {} ) saved to: {}".format(p.type_code, url))
        created = True
    else:
        prt("Not building {} package ({})".format(p.type_code, reason))

    if not should_build and p.exists():
        created = False
        url = extant_url_f(p)

    post_f()

    if nv_name:
        p.move_to_nv_name()

    return p, MetapackUrl(url, downloader=package_root.downloader), created


def make_excel_package(file, package_root, cache, env, force, nv_name=None, nv_link=False):
    assert package_root

    p = ExcelPackageBuilder(file, package_root, callback=prt, env=env)

    return _exec_build(p,
                       package_root, force, nv_name,
                       lambda p: p.package_path.path,
                       lambda: p.create_nv_link() if nv_link else None)


def make_zip_package(file, package_root, cache, env, force, nv_name=None, nv_link=False):
    assert package_root

    p = ZipPackageBuilder(file, package_root, callback=prt, env=env)

    return _exec_build(p,
                       package_root, force, nv_name,
                       lambda p: p.package_path.path,
                       lambda: p.create_nv_link() if nv_link else None)


def make_filesystem_package(file, package_root, cache, env, force, nv_name=None, nv_link=False, reuse_resources=False):
    from os.path import join

    assert package_root

    p = FileSystemPackageBuilder(file, package_root, callback=prt, env=env, reuse_resources=reuse_resources)

    return _exec_build(p,
                       package_root, force, nv_name,
                       lambda p: join(p.package_path.path.rstrip('/'), DEFAULT_METATAB_FILE),
                       lambda: p.create_nv_link() if nv_link else None)


def make_csv_package(file, package_root, cache, env, force, nv_name=None, nv_link=False):
    assert package_root

    p = CsvPackageBuilder(file, package_root, callback=prt, env=env)

    return _exec_build(p,
                       package_root, force, nv_name,
                       lambda p: p.package_path.path,
                       lambda: p.create_nv_link() if nv_link else None)


def set_distributions(doc, dist_urls):
    for t in doc.find('Root.Distribution'):
        doc.remove_term(t)

    for au in dist_urls:
        doc['Root'].new_term('Root.Distribution', au)

    write_doc(doc)()


def make_s3_package(file, package_root, cache, env, skip_if_exists, acl='public-read'):
    from metapack import MetapackUrl
    from metapack_build.package import S3PackageBuilder

    assert package_root

    p = S3PackageBuilder(file, package_root, callback=prt, env=env, acl=acl)

    if not p.exists() or not skip_if_exists:
        url = p.save()
        prt("Packaged saved to: {}".format(url))
        created = True
    elif p.exists():
        prt("S3 Filesystem Package already exists")
        created = False
        url = p.access_url

    return p, MetapackUrl(url, downloader=file.downloader), created


def create_s3_csv_package(m, dist_urls, fs_p):
    from metapack_build.package.csv import CsvPackageBuilder

    u = MetapackUrl(fs_p.access_url, downloader=m.downloader)

    resource_root = u.dirname().as_type(MetapackPackageUrl)

    p = CsvPackageBuilder(u, m.package_root, resource_root)

    access_url = m.bucket.access_url(p.cache_path)
    dist_urls.append(access_url)

    for au in dist_urls:
        if not p.doc.find_first('Root.Distribution', str(au)):
            p.doc['Root'].new_term('Root.Distribution', au)

    # Re-write the URLS for the datafiles
    for r in p.datafiles:
        r.url = fs_p.bucket.access_url(r.url)

    # Rewrite Documentation urls:
    for r in p.doc.find(['Root.Documentation', 'Root.Image']):

        url = parse_app_url(r.url)
        if url.proto == 'file':
            r.url = fs_p.bucket.access_url(url.path)

    csv_url = p.save()

    with open(csv_url.path, mode='rb') as f:
        m.bucket.write(f.read(), csv_url.target_file, m.acl)

    if m.bucket.last_reason:
        # Ugly encapsulation-breaking hack.
        fs_p.files_processed += [[*m.bucket.last_reason, access_url, '/'.join(csv_url.path.split(os.sep)[-2:])]]

    # Create an alternative url with no version number, so users can get the
    # most recent version
    csv_non_ver_url = csv_url.join_dir("{}.{}".format(m.doc.nonver_name, csv_url.target_format))

    with open(csv_url.path, mode='rb') as f:
        m.bucket.write(f.read(), csv_non_ver_url.target_file, m.acl)

    s3_path = csv_non_ver_url.path.split(os.sep)[-1]

    nv_access_url = m.bucket.access_url(s3_path)

    dist_urls.append(nv_access_url)

    if m.bucket.last_reason:
        # Ugly encapsulation-breaking hack.
        fs_p.files_processed += [[*m.bucket.last_reason, nv_access_url, s3_path]]

    return access_url


def generate_packages(m):
    for ptype, purl, cache_path in find_packages(m.doc.get_value('Root.Name'), m.package_root):
        yield ptype, purl, cache_path


def find_csv_packages(m, downloader):
    """Locate the build CSV package, which will have distributions if it was generated  as
    an S3 package"""
    from metapack_build.package import CsvPackageBuilder

    pkg_dir = m.package_root
    name = m.doc.get_value('Root.Name')

    package_path, cache_path = CsvPackageBuilder.make_package_path(pkg_dir, name)

    if package_path.exists():
        r = open_package(package_path, downloader=downloader)
        return r
