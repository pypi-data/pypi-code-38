# -*- coding: utf-8 -*-
# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>
#            Ralph Bean <rbean@redhat.com>
#            Matt Prahl <mprahl@redhat.com>

""" SQLAlchemy Database models for the Flask app
"""

import contextlib
import hashlib
import json
import re
from collections import OrderedDict
from datetime import datetime

import sqlalchemy
import kobo.rpmlib
from flask import has_app_context
from sqlalchemy import func, and_
from sqlalchemy.orm import lazyload
from sqlalchemy.orm import validates, scoped_session, sessionmaker, load_only

import module_build_service.messaging
from module_build_service import db, log, get_url_for, app, conf
from module_build_service.errors import UnprocessableEntity

DEFAULT_MODULE_CONTEXT = "00000000"


# Just like koji.BUILD_STATES, except our own codes for modules.
BUILD_STATES = {
    # This is (obviously) the first state a module build enters.
    #
    # When a user first submits a module build, it enters this state. We parse
    # the modulemd file, learn the NVR, create a record for the module build.
    # and publish the message.
    #
    # Then, we validate that the components are available, and that we can
    # fetch them. If this is all good, then we set the build to the 'wait'
    # state. If anything goes wrong, we jump immediately to the 'failed' state.
    "init": 0,
    # Here, the scheduler picks up tasks in wait and switches to build
    # immediately. Eventually, we'll add throttling logic here so we don't
    # submit too many builds for the build system to handle
    "wait": 1,
    # The scheduler works on builds in this state. We prepare the buildroot,
    # submit builds for all the components, and wait for the results to come
    # back.
    "build": 2,
    # Once all components have succeeded, we set the top-level module build
    # to 'done'.
    "done": 3,
    # If any of the component builds fail, then we set the top-level module
    # build to 'failed' also.
    "failed": 4,
    # This is a state to be set when a module is ready to be part of a
    # larger compose. perhaps it is set by an external service that knows
    # about the Grand Plan.
    "ready": 5,
    # If the module has failed and was garbage collected by MBS
    "garbage": 6,
}

INVERSE_BUILD_STATES = {v: k for k, v in BUILD_STATES.items()}


def _utc_datetime_to_iso(datetime_object):
    """
    Takes a UTC datetime object and returns an ISO formatted string
    :param datetime_object: datetime.datetime
    :return: string with datetime in ISO format
    """
    if datetime_object:
        # Converts the datetime to ISO 8601
        return datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")

    return None


@contextlib.contextmanager
def _dummy_context_mgr():
    """
    Yields None. Used in the make_session to not duplicate the code when
    app_context exists.
    """
    yield None


def _setup_event_listeners(session):
    """
    Starts listening for events related to database session.
    """
    if not sqlalchemy.event.contains(session, "before_commit", session_before_commit_handlers):
        sqlalchemy.event.listen(session, "before_commit", session_before_commit_handlers)

    # initialize DB event listeners from the monitor module
    from module_build_service.monitor import db_hook_event_listeners

    db_hook_event_listeners(session.bind.engine)


@contextlib.contextmanager
def make_session(conf):
    """
    Yields new SQLAlchemy database sesssion.
    """

    # Do not use scoped_session in case we are using in-memory database,
    # because we want to use the same session across all threads to be able
    # to use the same in-memory database in tests.
    if conf.sqlalchemy_database_uri == "sqlite://":
        _setup_event_listeners(db.session)
        yield db.session
        db.session.commit()
        return

    # Needs to be set to create app_context.
    if not has_app_context() and ("SERVER_NAME" not in app.config or not app.config["SERVER_NAME"]):
        app.config["SERVER_NAME"] = "localhost"

    # If there is no app_context, we have to create one before creating
    # the session. If we would create app_context after the session (this
    # happens in get_url_for() method), new concurrent session would be
    # created and this would lead to "database is locked" error for SQLite.
    with app.app_context() if not has_app_context() else _dummy_context_mgr():
        # TODO - we could use ZopeTransactionExtension() here some day for
        # improved safety on the backend.
        engine = sqlalchemy.engine_from_config({"sqlalchemy.url": conf.sqlalchemy_database_uri})
        session = scoped_session(sessionmaker(bind=engine))()
        _setup_event_listeners(session)
        try:
            yield session
            session.commit()
        except Exception:
            # This is a no-op if no transaction is in progress.
            session.rollback()
            raise
        finally:
            session.close()


class MBSBase(db.Model):
    # TODO -- we can implement functionality here common to all our model classes
    __abstract__ = True


module_builds_to_module_buildrequires = db.Table(
    "module_builds_to_module_buildrequires",
    db.Column("module_id", db.Integer, db.ForeignKey("module_builds.id"), nullable=False),
    db.Column(
        "module_buildrequire_id", db.Integer, db.ForeignKey("module_builds.id"), nullable=False),
    db.UniqueConstraint("module_id", "module_buildrequire_id", name="unique_buildrequires"),
)


module_builds_to_virtual_streams = db.Table(
    "module_builds_to_virtual_streams",
    db.Column("module_build_id", db.Integer, db.ForeignKey("module_builds.id"), nullable=False),
    db.Column("virtual_stream_id", db.Integer, db.ForeignKey("virtual_streams.id"), nullable=False),
    db.UniqueConstraint(
        "module_build_id", "virtual_stream_id", name="unique_module_to_virtual_stream"),
)


module_builds_to_arches = db.Table(
    "module_builds_to_arches",
    db.Column("module_build_id", db.Integer, db.ForeignKey("module_builds.id"), nullable=False),
    db.Column(
        "module_arch_id", db.Integer, db.ForeignKey("module_arches.id"),
        nullable=False),
    db.UniqueConstraint(
        "module_build_id", "module_arch_id", name="unique_module_to_arch"),
)


class ModuleBuild(MBSBase):
    __tablename__ = "module_builds"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    stream = db.Column(db.String, nullable=False)
    version = db.Column(db.String, nullable=False)
    ref_build_context = db.Column(db.String)
    build_context = db.Column(db.String)
    runtime_context = db.Column(db.String)
    context = db.Column(db.String, nullable=False, server_default=DEFAULT_MODULE_CONTEXT)
    state = db.Column(db.Integer, nullable=False)
    state_reason = db.Column(db.String)
    modulemd = db.Column(db.String, nullable=False)
    koji_tag = db.Column(db.String)  # This gets set after 'wait'
    # Koji tag to which tag the Content Generator Koji build.
    cg_build_koji_tag = db.Column(db.String)  # This gets set after wait
    scmurl = db.Column(db.String)
    scratch = db.Column(db.Boolean, default=False)
    # JSON encoded list of links of custom SRPMs uploaded to Koji
    srpms = db.Column(db.String)
    owner = db.Column(db.String, nullable=False)
    time_submitted = db.Column(db.DateTime, nullable=False)
    time_modified = db.Column(db.DateTime)
    time_completed = db.Column(db.DateTime)
    new_repo_task_id = db.Column(db.Integer)
    rebuild_strategy = db.Column(db.String, nullable=False)
    virtual_streams = db.relationship(
        "VirtualStream", secondary=module_builds_to_virtual_streams, back_populates="module_builds")

    # List of arches against which the module is built.
    # NOTE: It is not filled for imported modules, because imported module builds have not been
    # built by MBS.
    arches = db.relationship(
        "ModuleArch", secondary=module_builds_to_arches, back_populates="module_builds",
        order_by="ModuleArch.name")

    # A monotonically increasing integer that represents which batch or
    # iteration this module is currently on for successive rebuilds of its
    # components.  Think like 'mockchain --recurse'
    batch = db.Column(db.Integer, default=0)

    # This is only used for base modules for ordering purposes (f27.0.1 => 270001)
    stream_version = db.Column(db.Float)
    buildrequires = db.relationship(
        "ModuleBuild",
        secondary=module_builds_to_module_buildrequires,
        primaryjoin=module_builds_to_module_buildrequires.c.module_id == id,
        secondaryjoin=module_builds_to_module_buildrequires.c.module_buildrequire_id == id,
        backref="buildrequire_for",
    )

    rebuild_strategies = {
        "all": "All components will be rebuilt",
        "changed-and-after": (
            "All components that have changed and those in subsequent batches will be rebuilt"
        ),
        "only-changed": "All changed components will be rebuilt",
    }

    def current_batch(self, state=None):
        """ Returns all components of this module in the current batch. """

        if not self.batch:
            raise ValueError("No batch is in progress: %r" % self.batch)

        if state is not None:
            return [
                component for component in self.component_builds
                if component.batch == self.batch and component.state == state
            ]
        else:
            return [
                component for component in self.component_builds
                if component.batch == self.batch
            ]

    def last_batch_id(self):
        """ Returns the id of the last batch """
        return max([build.batch for build in self.component_builds])

    def up_to_current_batch(self, state=None):
        """
        Returns all components of this module in the current batch and
        in the previous batches.
        """

        if not self.batch:
            raise ValueError("No batch is in progress: %r" % self.batch)

        if state is not None:
            return [
                component for component in self.component_builds
                if component.batch <= self.batch and component.state == state
            ]
        else:
            return [
                component for component in self.component_builds if component.batch <= self.batch
            ]

    @staticmethod
    def get_by_id(session, module_build_id):
        """Find out a module build by id and return

        :param session: SQLAlchemy database session object.
        :param int module_build_id: the module build id to find out.
        :return: the found module build. None is returned if no module build
            with specified id in database.
        :rtype: :class:`ModuleBuild`
        """
        return session.query(ModuleBuild).filter(ModuleBuild.id == module_build_id).first()

    @staticmethod
    def get_last_build_in_all_streams(session, name):
        """
        Returns list of all latest ModuleBuilds in "ready" state for all
        streams for given module `name`.
        """
        # Prepare the subquery to find out all unique name:stream records.
        subq = (
            session.query(
                func.max(ModuleBuild.id).label("maxid"),
                func.max(sqlalchemy.cast(ModuleBuild.version, db.BigInteger)),
            )
            .group_by(ModuleBuild.stream)
            .filter_by(name=name, state=BUILD_STATES["ready"])
            .subquery("t2")
        )

        # Use the subquery to actually return all the columns for its results.
        query = session.query(ModuleBuild).join(subq, and_(ModuleBuild.id == subq.c.maxid))
        return query.all()

    @staticmethod
    def _get_last_builds_in_stream_query(session, name, stream, **kwargs):
        # Prepare the subquery to find out all unique name:stream records.
        subq = (
            session.query(
                func.max(sqlalchemy.cast(ModuleBuild.version, db.BigInteger)).label("maxversion")
            )
            .filter_by(name=name, state=BUILD_STATES["ready"], stream=stream, **kwargs)
            .subquery("t2")
        )

        # Use the subquery to actually return all the columns for its results.
        query = session.query(ModuleBuild).join(
            subq,
            and_(
                ModuleBuild.name == name,
                ModuleBuild.stream == stream,
                sqlalchemy.cast(ModuleBuild.version, db.BigInteger) == subq.c.maxversion,
            ),
        )
        return query

    @staticmethod
    def get_last_builds_in_stream(session, name, stream, virtual_streams=None, **kwargs):
        """
        Returns the latest builds in "ready" state for given name:stream.

        :param session: SQLAlchemy session.
        :param str name: Name of the module to search builds for.
        :param str stream: Stream of the module to search builds for.
        :param list virtual_streams: a list of the virtual streams to filter on. The filtering uses
            "or" logic. When falsy, no filtering occurs.
        :param dict kwargs: Key/value pairs passed to SQLAlchmey filter_by method
            allowing to set additional filter for results.

        """
        # Prepare the subquery to find out all unique name:stream records.

        query = ModuleBuild._get_last_builds_in_stream_query(session, name, stream, **kwargs)
        query = ModuleBuild._add_virtual_streams_filter(session, query, virtual_streams)
        return query.all()

    @staticmethod
    def get_last_build_in_stream(session, name, stream, **kwargs):
        """
        Returns the latest build in "ready" state for given name:stream.

        :param session: SQLAlchemy session.
        :param str name: Name of the module to search builds for.
        :param str stream: Stream of the module to search builds for.
        :param dict kwargs: Key/value pairs passed to SQLAlchmey filter_by method
            allowing to set additional filter for results.
        """
        return ModuleBuild._get_last_builds_in_stream_query(session, name, stream, **kwargs).first()

    @staticmethod
    def get_build_from_nsvc(session, name, stream, version, context, **kwargs):
        """
        Returns build defined by NSVC. Optional kwargs are passed to SQLAlchemy
        filter_by method.
        """
        return (
            session.query(ModuleBuild)
            .filter_by(name=name, stream=stream, version=str(version), context=context, **kwargs)
            .first()
        )

    @staticmethod
    def get_scratch_builds_from_nsvc(session, name, stream, version, context, **kwargs):
        """
        Returns all scratch builds defined by NSVC. This is done by using the supplied `context`
        as a match prefix. Optional kwargs are passed to SQLAlchemy filter_by method.
        """
        return (
            session.query(ModuleBuild)
            .filter_by(name=name, stream=stream, version=str(version), scratch=True, **kwargs)
            .filter(ModuleBuild.context.like(context + "%"))
            .all()
        )

    @staticmethod
    def _add_stream_version_lte_filter(session, query, stream_version):
        """
        Adds a less than or equal to filter for stream versions based on x.y.z versioning.

        In essence, the filter does `XX0000 <= stream_version <= XXYYZZ`

        :param session: a SQLAlchemy session
        :param query: a SQLAlchemy query to add the filtering to
        :param int stream_version: the stream version to filter on
        :return: the query with the added stream version filter
        """
        if not stream_version:
            return query

        # Compute the minimal stream_version. For example, for `stream_version` 281234,
        # the minimal `stream_version` is 280000.
        min_stream_version = (stream_version // 10000) * 10000
        return query.filter(ModuleBuild.stream_version <= stream_version).filter(
            ModuleBuild.stream_version >= min_stream_version)

    @staticmethod
    def _add_virtual_streams_filter(session, query, virtual_streams):
        """
        Adds a filter on ModuleBuild.virtual_streams to an existing query.

        :param session: a SQLAlchemy session
        :param query: a SQLAlchemy query to add the filtering to
        :param list virtual_streams: a list of the virtual streams to filter on. The filtering uses
            "or" logic. When falsy, no filtering occurs.
        :return: the query with the added virtual stream filters
        """
        if not virtual_streams:
            return query

        # Create a subquery that filters down all the module builds that contain the virtual
        # streams. Using distinct is necessary since a module build may contain multiple virtual
        # streams that are desired.
        modules_with_virtual_streams = (
            session.query(ModuleBuild)
            .join(VirtualStream, ModuleBuild.virtual_streams)
            .filter(VirtualStream.name.in_(virtual_streams))
            .order_by(ModuleBuild.id)
            .distinct(ModuleBuild.id)
        ).subquery()

        # Join the original query with the subquery so that only module builds with the desired
        # virtual streams remain
        return query.join(
            modules_with_virtual_streams, ModuleBuild.id == modules_with_virtual_streams.c.id)

    @staticmethod
    def get_last_builds_in_stream_version_lte(
            session, name, stream_version=None, virtual_streams=None):
        """
        Returns the latest builds in "ready" state for given name:stream limited by
        `stream_version`. The `stream_version` is int generated by `get_stream_version(...)`
        method from "x.y.z" version string.
        The builds returned by this method are limited by stream_version XX.YY.ZZ like this:
            "XX0000 <= build.stream_version <= XXYYZZ".

        :param session: SQLAlchemy session.
        :param str name: Name of the module to search builds for.
        :param int stream_version: Maximum stream_version to search builds for. When None,
            the stream_version is not limited.
        :param list virtual_streams: A list of the virtual streams to filter on. The filtering uses
            "or" logic. When falsy, no filtering occurs.
        """
        query = (
            session.query(ModuleBuild)
            .filter(ModuleBuild.name == name)
            .filter(ModuleBuild.state == BUILD_STATES["ready"])
            .order_by(sqlalchemy.cast(ModuleBuild.version, db.BigInteger).desc())
        )

        query = ModuleBuild._add_stream_version_lte_filter(session, query, stream_version)
        query = ModuleBuild._add_virtual_streams_filter(session, query, virtual_streams)

        builds = query.all()

        # In case there are multiple versions of single name:stream build, we want to return
        # the latest version only. The `builds` are ordered by "version" desc, so we
        # can just get the first (greatest) version of name:stream.
        # TODO: Is there a way how to do that nicely in the SQL query itself?
        seen = {}  # {"n:s": v, ...}
        ret = []
        for build in builds:
            ns = "%s:%s" % (build.name, build.stream)
            if ns in seen and seen[ns] != build.version:
                # Skip the builds if we already handled this nsv before.
                continue
            elif ns in seen and seen[ns] == build.version:
                # Different context of the NSV
                ret.append(build)
                continue

            seen[ns] = build.version
            ret.append(build)
        return ret

    @staticmethod
    def get_module_count(session, **kwargs):
        """
        Determine the number of modules that match the provided filter.

        :param session: SQLAlchemy session
        :return: the number of modules that match the provided filter
        :rtype: int
        """
        return session.query(func.count(ModuleBuild.id)).filter_by(**kwargs).scalar()

    @staticmethod
    def get_build_by_koji_tag(session, tag):
        """Get build by its koji_tag"""
        return session.query(ModuleBuild).filter_by(koji_tag=tag).first()

    def mmd(self):
        from module_build_service.utils import load_mmd

        try:
            return load_mmd(self.modulemd)
        except UnprocessableEntity:
            log.exception("An error occurred while trying to parse the modulemd")
            raise ValueError("Invalid modulemd")

    @property
    def previous_non_failed_state(self):
        for trace in reversed(self.module_builds_trace):
            if trace.state != BUILD_STATES["failed"]:
                return trace.state

    @validates("state")
    def validate_state(self, key, field):
        if field in BUILD_STATES.values():
            return field
        if field in BUILD_STATES:
            return BUILD_STATES[field]
        raise ValueError("%s: %s, not in %r" % (key, field, BUILD_STATES))

    @validates("rebuild_strategy")
    def validate_rebuild_stategy(self, key, rebuild_strategy):
        if rebuild_strategy not in self.rebuild_strategies.keys():
            choices = ", ".join(self.rebuild_strategies.keys())
            raise ValueError(
                'The rebuild_strategy of "{0}" is invalid. Choose from: {1}'.format(
                    rebuild_strategy, choices)
            )
        return rebuild_strategy

    @classmethod
    def from_module_event(cls, session, event):
        if type(event) == module_build_service.messaging.MBSModule:
            return session.query(cls).filter(cls.id == event.module_build_id).first()
        else:
            raise ValueError("%r is not a module message." % type(event).__name__)

    @staticmethod
    def contexts_from_mmd(mmd_str):
        """
        Returns tuple (ref_build_context, build_context, runtime_context, context)
        with hashes:
            - ref_build_context - Hash of commit hashes of expanded buildrequires.
            - build_context - Hash of stream names of expanded buildrequires.
            - runtime_context - Hash of stream names of expanded runtime requires.
            - context - Hash of combined hashes of build_context and runtime_context.

        :param str mmd_str: String with Modulemd metadata.
        :rtype: tuple of strings
        :return: Tuple with build_context, strem_build_context, runtime_context and
                 context hashes.
        """
        from module_build_service.utils.general import load_mmd

        try:
            mmd = load_mmd(mmd_str)
        except UnprocessableEntity:
            raise ValueError("Invalid modulemd")
        mbs_xmd = mmd.get_xmd().get("mbs", {})
        rv = []

        # Get the buildrequires from the XMD section, because it contains
        # all the buildrequires as we resolved them using dependency resolver.
        if "buildrequires" not in mbs_xmd:
            raise ValueError("The module's modulemd hasn't been formatted by MBS")
        mmd_formatted_buildrequires = {
            dep: info["ref"] for dep, info in mbs_xmd["buildrequires"].items()
        }
        property_json = json.dumps(OrderedDict(sorted(mmd_formatted_buildrequires.items())))
        rv.append(hashlib.sha1(property_json.encode("utf-8")).hexdigest())

        # Get the streams of buildrequires and hash it.
        mmd_formatted_buildrequires = {
            dep: info["stream"] for dep, info in mbs_xmd["buildrequires"].items()
        }
        property_json = json.dumps(OrderedDict(sorted(mmd_formatted_buildrequires.items())))
        build_context = hashlib.sha1(property_json.encode("utf-8")).hexdigest()
        rv.append(build_context)

        # Get the requires from the real "dependencies" section in MMD.
        mmd_requires = {}
        for deps in mmd.get_dependencies():
            for name in deps.get_runtime_modules():
                streams = deps.get_runtime_streams(name)
                if name not in mmd_requires:
                    mmd_requires[name] = set()
                mmd_requires[name] = mmd_requires[name].union(streams)

        # Sort the streams for each module name and also sort the module names.
        mmd_requires = {dep: sorted(list(streams)) for dep, streams in mmd_requires.items()}
        property_json = json.dumps(OrderedDict(sorted(mmd_requires.items())))
        runtime_context = hashlib.sha1(property_json.encode("utf-8")).hexdigest()
        rv.append(runtime_context)

        combined_hashes = "{0}:{1}".format(build_context, runtime_context)
        context = hashlib.sha1(combined_hashes.encode("utf-8")).hexdigest()[:8]
        rv.append(context)

        return tuple(rv)

    @property
    def siblings(self):
        query = (
            self.query.filter_by(
                name=self.name, stream=self.stream, version=self.version, scratch=self.scratch)
            .options(load_only("id"))
            .filter(ModuleBuild.id != self.id)
        )
        return [build.id for build in query.all()]

    @property
    def nvr(self):
        return {
            u"name": self.name,
            u"version": self.stream.replace("-", "_"),
            u"release": "{0}.{1}".format(self.version, self.context)
        }

    @property
    def nvr_string(self):
        return kobo.rpmlib.make_nvr(self.nvr)

    @classmethod
    def create(
        cls,
        session,
        conf,
        name,
        stream,
        version,
        modulemd,
        scmurl,
        username,
        context=None,
        rebuild_strategy=None,
        scratch=False,
        srpms=None,
        publish_msg=True,
        **kwargs
    ):
        now = datetime.utcnow()
        module = cls(
            name=name,
            stream=stream,
            version=version,
            context=context,
            state="init",
            modulemd=modulemd,
            scmurl=scmurl,
            owner=username,
            time_submitted=now,
            time_modified=now,
            # If the rebuild_strategy isn't specified, use the default
            rebuild_strategy=rebuild_strategy or conf.rebuild_strategy,
            scratch=scratch,
            srpms=json.dumps(srpms or []),
            **kwargs
        )
        # Add a state transition to "init"
        mbt = ModuleBuildTrace(state_time=now, state=module.state)
        module.module_builds_trace.append(mbt)

        # Record the base modules this module buildrequires
        for base_module in module.get_buildrequired_base_modules(session):
            module.buildrequires.append(base_module)

        session.add(module)
        session.commit()
        if publish_msg:
            module_build_service.messaging.publish(
                service="mbs",
                topic="module.state.change",
                msg=module.json(show_tasks=False),  # Note the state is "init" here...
                conf=conf,
            )
        return module

    def transition(self, conf, state, state_reason=None, failure_type="unspec"):
        """Record that a build has transitioned state.

        The history of state transitions are recorded in model
        ``ModuleBuildTrace``. If transform to a different state, for example
        from ``build`` to ``done``, message will be sent to configured message
        bus.

        :param conf: MBS config object returned from function :func:`init_config`
            which contains loaded configs.
        :type conf: :class:`Config`
        :param int state: the state value to transition to. Refer to ``BUILD_STATES``.
        :param str state_reason: optional reason of why to transform to ``state``.
        :param str failure_reason: optional failure type: 'unspec', 'user', 'infra'
        """
        now = datetime.utcnow()
        old_state = self.state
        self.state = state
        self.time_modified = now

        from module_build_service.monitor import builder_success_counter, builder_failed_counter

        if INVERSE_BUILD_STATES[self.state] in ["done", "failed"]:
            self.time_completed = now
            if INVERSE_BUILD_STATES[self.state] == "done":
                builder_success_counter.inc()
            else:
                builder_failed_counter.labels(reason=failure_type).inc()

        if state_reason:
            self.state_reason = state_reason

        # record module's state change
        mbt = ModuleBuildTrace(state_time=now, state=self.state, state_reason=state_reason)
        self.module_builds_trace.append(mbt)

        log.info("%r, state %r->%r" % (self, old_state, self.state))
        if old_state != self.state:
            module_build_service.messaging.publish(
                service="mbs",
                topic="module.state.change",
                msg=self.json(show_tasks=False),
                conf=conf,
            )

    @classmethod
    def local_modules(cls, session, name=None, stream=None):
        """
        Returns list of local module builds added by
        utils.load_local_builds(...). When `name` or `stream` is set,
        it is used to further limit the result set.

        If conf.system is not set to "mock" or "test", returns empty
        list everytime, because local modules make sense only when
        building using Mock backend or during tests.
        """
        if conf.system in ["koji"]:
            return []

        filters = {}
        if name:
            filters["name"] = name
        if stream:
            filters["stream"] = stream
        local_modules = session.query(ModuleBuild).filter_by(**filters).all()
        if not local_modules:
            return []

        local_modules = [
            m for m in local_modules if m.koji_tag and m.koji_tag.startswith(conf.mock_resultsdir)
        ]
        return local_modules

    @classmethod
    def by_state(cls, session, state):
        return session.query(ModuleBuild).filter_by(state=BUILD_STATES[state]).all()

    @classmethod
    def from_repo_done_event(cls, session, event):
        """ Find the ModuleBuilds in our database that should be in-flight...
        ... for a given koji tag.

        There should be at most one.
        """
        if event.repo_tag.endswith("-build"):
            tag = event.repo_tag[:-6]
        else:
            tag = event.repo_tag
        query = (
            session.query(cls)
            .filter(cls.koji_tag == tag)
            .filter(cls.state == BUILD_STATES["build"])
        )

        count = query.count()
        if count > 1:
            raise RuntimeError("%r module builds in flight for %r" % (count, tag))

        return query.first()

    @classmethod
    def from_tag_change_event(cls, session, event):
        tag = event.tag[:-6] if event.tag.endswith("-build") else event.tag
        query = (
            session.query(cls)
            .filter(cls.koji_tag == tag)
            .filter(cls.state == BUILD_STATES["build"])
        )

        count = query.count()
        if count > 1:
            raise RuntimeError("%r module builds in flight for %r" % (count, tag))

        return query.first()

    def short_json(self, show_stream_version=False, show_scratch=True):
        rv = {
            "id": self.id,
            "state": self.state,
            "state_name": INVERSE_BUILD_STATES[self.state],
            "stream": self.stream,
            "version": self.version,
            "name": self.name,
            "context": self.context,
        }
        if show_stream_version:
            rv["stream_version"] = self.stream_version
        if show_scratch:
            rv["scratch"] = self.scratch
        return rv

    def json(self, show_tasks=True):
        mmd = self.mmd()
        xmd = mmd.get_xmd()
        buildrequires = xmd.get("mbs", {}).get("buildrequires", {})
        rv = self.short_json()
        rv.update({
            "component_builds": [build.id for build in self.component_builds],
            "koji_tag": self.koji_tag,
            "owner": self.owner,
            "rebuild_strategy": self.rebuild_strategy,
            "scmurl": self.scmurl,
            "srpms": json.loads(self.srpms or "[]"),
            "siblings": self.siblings,
            "state_reason": self.state_reason,
            "time_completed": _utc_datetime_to_iso(self.time_completed),
            "time_modified": _utc_datetime_to_iso(self.time_modified),
            "time_submitted": _utc_datetime_to_iso(self.time_submitted),
            "buildrequires": buildrequires,
        })
        if show_tasks:
            rv["tasks"] = self.tasks()
        return rv

    def extended_json(self, show_state_url=False, api_version=1):
        """
        :kwarg show_state_url: this will determine if `get_url_for` should be run to determine
        what the `state_url` is. This should be set to `False` when extended_json is called from
        the backend because it forces an app context to be created, which causes issues with
        SQLAlchemy sessions.
        :kwarg api_version: the API version to use when building the state URL
        """
        rv = self.json(show_tasks=True)
        state_url = None
        if show_state_url:
            state_url = get_url_for("module_build", api_version=api_version, id=self.id)

        rv.update({
            "base_module_buildrequires": [br.short_json(True, False) for br in self.buildrequires],
            "build_context": self.build_context,
            "modulemd": self.modulemd,
            "ref_build_context": self.ref_build_context,
            "runtime_context": self.runtime_context,
            "state_trace": [
                {
                    "time": _utc_datetime_to_iso(record.state_time),
                    "state": record.state,
                    "state_name": INVERSE_BUILD_STATES[record.state],
                    "reason": record.state_reason,
                }
                for record in self.state_trace(self.id)
            ],
            "state_url": state_url,
            "stream_version": self.stream_version,
            "virtual_streams": [virtual_stream.name for virtual_stream in self.virtual_streams],
            "arches": [arch.name for arch in self.arches],
        })

        return rv

    def tasks(self):
        """
        :return: dictionary containing the tasks associated with the build
        """
        tasks = dict()
        if self.id and self.state != "init":
            for build in (
                ComponentBuild.query.filter_by(module_id=self.id)
                .options(lazyload("module_build"))
                .all()
            ):
                tasks[build.format] = tasks.get(build.format, {})
                tasks[build.format][build.package] = dict(
                    task_id=build.task_id,
                    state=build.state,
                    state_reason=build.state_reason,
                    nvr=build.nvr,
                    # TODO -- it would be really nice from a UX PoV to get a
                    # link to the remote task here.
                )

        return tasks

    def state_trace(self, module_id):
        return (
            ModuleBuildTrace.query.filter_by(module_id=module_id)
            .order_by(ModuleBuildTrace.state_time)
            .all()
        )

    @staticmethod
    def get_stream_version(stream, right_pad=True):
        """
        Parse the supplied stream to find its version.

        This will parse a stream such as "f27" and return 270000. Another example would be a stream
        of "f27.0.1" and return 270001.
        :param str stream: the module stream
        :kwarg bool right_pad: determines if the right side of the stream version should be padded
            with zeroes (e.g. `f27` => `27` vs `270000`)
        :return: a stream version represented as a float. Stream suffix could
            be added according to config ``stream_suffixes``.
        :rtype: float or None if the stream doesn't have a valid version
        """
        # The platform version (e.g. prefix1.2.0 => 010200)
        version = ""
        for char in stream:
            # See if the current character is an integer, signifying the version has started
            if char.isdigit():
                version += char
            # If version isn't set, then a digit hasn't been encountered
            elif version:
                # If the character is a period and the version is set, then
                # the loop is still processing the version part of the stream
                if char == ".":
                    version += "."
                # If the version is set and the character is not a period or
                # digit, then the remainder of the stream is a suffix like "-beta"
                else:
                    break

        # Remove the periods and pad the numbers if necessary
        version = "".join([section.zfill(2) for section in version.rstrip(".").split(".")])

        if version:
            if right_pad:
                version += (6 - len(version)) * "0"

            result = float(version)

            for regexp, suffix in conf.stream_suffixes.items():
                if re.match(regexp, stream):
                    result += suffix
                    break

            return result

    def get_buildrequired_base_modules(self, session):
        """
        Find the base modules in the modulemd's xmd section.

        :param session: the SQLAlchemy database session to use to query
        :return: a list of ModuleBuild objects of the base modules that are buildrequired with the
            ordering in conf.base_module_names preserved
        :rtype: list
        :raises RuntimeError: when the xmd section isn't properly filled out by MBS
        """
        rv = []
        xmd = self.mmd().get_xmd()
        for bm in conf.base_module_names:
            try:
                bm_dict = xmd["mbs"]["buildrequires"].get(bm)
            except KeyError:
                raise RuntimeError("The module's mmd is missing information in the xmd section")

            if not bm_dict:
                continue
            base_module = self.get_build_from_nsvc(
                session, bm, bm_dict["stream"], bm_dict["version"], bm_dict["context"]
            )
            if not base_module:
                log.error(
                    'Module #{} buildrequires "{}" but it wasn\'t found in the database'.format(
                        self.id, repr(bm_dict))
                )
                continue
            rv.append(base_module)

        return rv

    def __repr__(self):
        return (
            "<ModuleBuild %s, id=%d, stream=%s, version=%s, scratch=%r,"
            " state %r, batch %r, state_reason %r>"
        ) % (
            self.name,
            self.id,
            self.stream,
            self.version,
            self.scratch,
            INVERSE_BUILD_STATES[self.state],
            self.batch,
            self.state_reason,
        )


class VirtualStream(MBSBase):
    __tablename__ = "virtual_streams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    module_builds = db.relationship(
        "ModuleBuild", secondary=module_builds_to_virtual_streams, back_populates="virtual_streams"
    )

    def __repr__(self):
        return "<VirtualStream id={} name={}>".format(self.id, self.name)


class ModuleArch(MBSBase):
    __tablename__ = "module_arches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    module_builds = db.relationship(
        "ModuleBuild", secondary=module_builds_to_arches, back_populates="arches"
    )

    def __repr__(self):
        return "<ModuleArch id={} name={}>".format(self.id, self.name)


class ModuleBuildTrace(MBSBase):
    __tablename__ = "module_builds_trace"
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module_builds.id"), nullable=False)
    state_time = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Integer, nullable=True)
    state_reason = db.Column(db.String, nullable=True)

    module_build = db.relationship("ModuleBuild", backref="module_builds_trace", lazy=False)

    def json(self):
        retval = {
            "id": self.id,
            "module_id": self.module_id,
            "state_time": _utc_datetime_to_iso(self.state_time),
            "state": self.state,
            "state_reason": self.state_reason,
        }

        return retval

    def __repr__(self):
        return (
            "<ModuleBuildTrace %s, module_id: %s, state_time: %r, state: %s, state_reason: %s>"
            % (self.id, self.module_id, self.state_time, self.state, self.state_reason)
        )


class ComponentBuild(MBSBase):
    __tablename__ = "component_builds"
    id = db.Column(db.Integer, primary_key=True)
    package = db.Column(db.String, nullable=False)
    scmurl = db.Column(db.String, nullable=False)
    # XXX: Consider making this a proper ENUM
    format = db.Column(db.String, nullable=False)
    task_id = db.Column(db.Integer)  # This is the id of the build in koji
    # This is the commit hash that component was built with
    ref = db.Column(db.String, nullable=True)
    # XXX: Consider making this a proper ENUM (or an int)
    state = db.Column(db.Integer)
    # Reason why the build failed
    state_reason = db.Column(db.String)
    # This stays as None until the build completes.
    nvr = db.Column(db.String)
    # True when this component build is tagged into buildroot (-build tag).
    tagged = db.Column(db.Boolean, default=False)
    # True when this component build is tagged into final tag.
    tagged_in_final = db.Column(db.Boolean, default=False)
    # True when this component build is build-time only (should be tagged only
    # to -build tag)
    build_time_only = db.Column(db.Boolean, default=False)

    # A monotonically increasing integer that represents which batch or
    # iteration this *component* is currently in.  This relates to the owning
    # module's batch.  This one defaults to None, which means that this
    # component is not currently part of a batch.
    batch = db.Column(db.Integer, default=0)

    module_id = db.Column(db.Integer, db.ForeignKey("module_builds.id"), nullable=False)
    module_build = db.relationship("ModuleBuild", backref="component_builds", lazy=False)
    reused_component_id = db.Column(db.Integer, db.ForeignKey("component_builds.id"))

    # Weight defines the complexity of the component build as calculated by the builder's
    # get_build_weights function
    weight = db.Column(db.Float, default=0)

    @classmethod
    def from_component_event(cls, session, event):
        if isinstance(event, module_build_service.messaging.KojiBuildChange):
            if event.module_build_id:
                return (
                    session.query(cls)
                    .filter_by(task_id=event.task_id, module_id=event.module_build_id)
                    .one()
                )
            else:
                return session.query(cls).filter(cls.task_id == event.task_id).first()
        else:
            raise ValueError("%r is not a koji message." % event["topic"])

    @classmethod
    def from_component_name(cls, session, component_name, module_id):
        return session.query(cls).filter_by(package=component_name, module_id=module_id).first()

    @classmethod
    def from_component_nvr(cls, session, nvr, module_id):
        return session.query(cls).filter_by(nvr=nvr, module_id=module_id).first()

    def state_trace(self, component_id):
        return (
            ComponentBuildTrace.query.filter_by(component_id=component_id)
            .order_by(ComponentBuildTrace.state_time)
            .all()
        )

    def json(self):
        retval = {
            "id": self.id,
            "package": self.package,
            "format": self.format,
            "task_id": self.task_id,
            "state": self.state,
            "state_reason": self.state_reason,
            "module_build": self.module_id,
            "nvr": self.nvr,
        }

        try:
            # Koji is py2 only, so this fails if the main web process is
            # running on py3.
            import koji

            retval["state_name"] = koji.BUILD_STATES.get(self.state)
        except ImportError:
            pass

        return retval

    def extended_json(self, show_state_url=False, api_version=1):
        """
        :kwarg show_state_url: this will determine if `get_url_for` should be run to determine
        what the `state_url` is. This should be set to `False` when extended_json is called from
        the backend because it forces an app context to be created, which causes issues with
        SQLAlchemy sessions.
        :kwarg api_version: the API version to use when building the state URL
        """
        json = self.json()
        state_url = None
        if show_state_url:
            state_url = get_url_for("component_build", api_version=api_version, id=self.id)
        json.update({
            "batch": self.batch,
            "state_trace": [
                {
                    "time": _utc_datetime_to_iso(record.state_time),
                    "state": record.state,
                    "state_name": INVERSE_BUILD_STATES[record.state],
                    "reason": record.state_reason,
                }
                for record in self.state_trace(self.id)
            ],
            "state_url": state_url,
        })

        return json

    def __repr__(self):
        return "<ComponentBuild %s, %r, state: %r, task_id: %r, batch: %r, state_reason: %s>" % (
            self.package,
            self.module_id,
            self.state,
            self.task_id,
            self.batch,
            self.state_reason,
        )


class ComponentBuildTrace(MBSBase):
    __tablename__ = "component_builds_trace"
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey("component_builds.id"), nullable=False)
    state_time = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Integer, nullable=True)
    state_reason = db.Column(db.String, nullable=True)
    task_id = db.Column(db.Integer, nullable=True)

    component_build = db.relationship(
        "ComponentBuild", backref="component_builds_trace", lazy=False
    )

    def json(self):
        retval = {
            "id": self.id,
            "component_id": self.component_id,
            "state_time": _utc_datetime_to_iso(self.state_time),
            "state": self.state,
            "state_reason": self.state_reason,
            "task_id": self.task_id,
        }

        return retval

    def __repr__(self):
        return (
            "<ComponentBuildTrace %s, component_id: %s, state_time: %r, state: %s,"
            " state_reason: %s, task_id: %s>"
        ) % (
            self.id,
            self.component_id,
            self.state_time,
            self.state,
            self.state_reason,
            self.task_id,
        )


def session_before_commit_handlers(session):
    # new and updated items
    for item in set(session.new) | set(session.dirty):
        # handlers for component builds
        if isinstance(item, ComponentBuild):
            cbt = ComponentBuildTrace(
                state_time=datetime.utcnow(),
                state=item.state,
                state_reason=item.state_reason,
                task_id=item.task_id,
            )
            # To fully support append, the hook must be tied to the session
            item.component_builds_trace.append(cbt)


@sqlalchemy.event.listens_for(ModuleBuild, "before_insert")
@sqlalchemy.event.listens_for(ModuleBuild, "before_update")
def new_and_update_module_handler(mapper, session, target):
    # Only modify time_modified if it wasn't explicitly set
    if not db.inspect(target).get_history("time_modified", True).has_changes():
        target.time_modified = datetime.utcnow()
