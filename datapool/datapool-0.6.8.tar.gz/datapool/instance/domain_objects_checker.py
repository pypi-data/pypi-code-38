# encoding: utf-8
from __future__ import absolute_import, division, print_function

from collections import Counter, OrderedDict
from os.path import join

from datapool.database import create_session
from datapool.errors import ConsistencyError

from .domain_objects import Parameters, Site, Source, SourceType
from .landing_zone_structure import lookup_checker, lookup_parser


def _report_duplicate_names(domain_objects):
    counter = Counter(obj.name for obj in domain_objects)
    for (name, count) in counter.items():
        if count > 1:
            yield name


def _unique_file_name(domain_objects):
    file_names = set(obj.file_name for obj in domain_objects)
    if len(file_names) > 1:
        raise RuntimeError(
            "different filenames for sites detected: {}".format(file_names)
        )
    file_name = file_names.pop()
    return file_name


def check_parameters_integrity(file_name, root_folder, domain_objects, session):
    if len(domain_objects) != 1:
        for domain_object in domain_objects:
            full_path = join(root_folder, domain_object.rel_path)
            yield ConsistencyError(
                "found multiple {}. one is at {}".format(file_name, full_path)
            )
        return
    parameters = domain_objects[0]
    full_path = join(root_folder, parameters.rel_path)
    for name in _report_duplicate_names(parameters):
        yield ConsistencyError("name {} duplicate in {}".format(name, full_path))


def check_sites_integrity(file_name, root_folder, site_objects, session):
    for name in _report_duplicate_names(site_objects):
        yield ConsistencyError(
            "duplicate names: name {} appears in {}".format(name, file_name)
        )


def check_source_types_integrity(file_name, root_folder, source_type_objects, session):
    for name in _report_duplicate_names(source_type_objects):
        yield ConsistencyError(
            "duplicate names: name {} appears in {}".format(name, file_name)
        )
    from .source_type_model import fetch_existing_source_type_dbos, check_differences

    source_type_dbos = fetch_existing_source_type_dbos(session)
    removed = set(s.name for s in source_type_dbos) - set(
        s.name for s in source_type_objects
    )
    for r in removed:
        yield ConsistencyError(
            "source type {} is present in db, but removed in landing zone".format(r)
        )


def check_source_integrity(file_name, root_folder, source_type_objects, session):
    """return + yield defines an empty generator"""
    return
    yield


class DomainObjectsChecker:

    integrity_checkers = {
        Parameters: check_parameters_integrity,
        Site: check_sites_integrity,
        SourceType: check_source_types_integrity,
        Source: check_source_integrity,
    }

    def __init__(self, root_folder, rel_paths):
        self.root_folder = root_folder
        self.rel_paths = rel_paths
        self.domain_objects = OrderedDict()
        self.loaded = False

    def check_all(self, engine):
        yield from self.load_and_check_yamls()
        yield from self.check_integrity(engine)
        yield from self.check_against_temporal_db(engine)

    def load_and_check_yamls(self):
        for rel_path in self.rel_paths:
            checker = lookup_checker(rel_path)
            parser = lookup_parser(rel_path)
            if parser is None:
                full_path = join(self.root_folder, rel_path)
                yield ConsistencyError(
                    "can not parse {}. maybe file is at wrong position or "
                    "name is misspelled.".format(full_path)
                )
                continue
            if checker is None:
                full_path = join(self.root_folder, rel_path)
                yield ConsistencyError(
                    "can not check {}. maybe file is at wrong position or "
                    "name is misspelled.".format(full_path)
                )
                continue
            results = parser(self.root_folder, rel_path)
            for result in results:
                if isinstance(result, Exception):
                    yield result
                else:
                    key = result.__class__
                    if key not in self.domain_objects:
                        self.domain_objects[key] = []
                    self.domain_objects[key].append(result)
                    self.loaded = True

    def check_integrity(self, engine):
        session = create_session(engine)
        for domain_object_class, objects in self.domain_objects.items():
            integrity_checker = self.integrity_checkers[domain_object_class]
            file_name = _unique_file_name(objects)
            yield from integrity_checker(file_name, self.root_folder, objects, session)
        session.close()

    def check_against_temporal_db(self, session):
        from .landing_zone_structure import lookup_checker, lookup_committer

        for domain_objects in self.domain_objects.values():
            for domain_object in domain_objects:
                checker = lookup_checker(domain_object.rel_path)
                if checker is None:
                    # was checked in load_and_check_yamls
                    continue
                ok = True
                for check_result in checker(domain_object, session):
                    if isinstance(check_result, Exception):
                        yield check_result
                        ok = False
                if ok:
                    committer = lookup_committer(domain_object.rel_path)
                    committer(domain_object, session)
