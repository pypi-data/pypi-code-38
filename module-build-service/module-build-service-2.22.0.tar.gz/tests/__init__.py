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
# Written by Matt Prahl <mprahl@redhat.com

import os
from datetime import datetime, timedelta
from mock import patch
import time
import hashlib
from traceback import extract_stack
from module_build_service.utils import to_text_type, load_mmd_file

import koji
import module_build_service
from module_build_service import db
from module_build_service.utils import get_rpm_release, import_mmd, mmd_to_str
from module_build_service.config import init_config
from module_build_service.models import (
    ModuleBuild, ComponentBuild, VirtualStream, make_session, BUILD_STATES,
)
from module_build_service import Modulemd


base_dir = os.path.dirname(__file__)
app = module_build_service.app
conf = init_config(app)


def read_staged_data(yaml_name):
    """Read module YAML content from staged_data directory

    :param str yaml_name: name of YAML file without extension ``.yaml``.
    :return: module YAML file's content.
    :rtype: str
    :raises ValueError: if specified module YAML file does not exist in
        staged_data directory.
    """
    filename = os.path.join(base_dir, "staged_data", "{}.yaml".format(yaml_name))
    if not os.path.exists(filename):
        raise ValueError("Staged data {}.yaml does not exist.".format(yaml_name))
    with open(filename, "r") as mmd:
        return to_text_type(mmd.read())


def patch_config():
    # add test builders for all resolvers
    with_test_builders = dict()
    for k, v in module_build_service.config.SUPPORTED_RESOLVERS.items():
        v["builders"].extend(["test", "testlocal"])
        with_test_builders[k] = v
    patch("module_build_service.config.SUPPORTED_RESOLVERS", with_test_builders)


patch_config()


def patch_zeromq_time_sleep():
    """
    We use moksha.hub in some tests. We used dummy zerombq backend which
    connects to /dev/null, but zeromq.py contains time.sleep(1) to ensure
    that sockets are listening properly. This is not needed for our dummy
    use-case and it slows down tests.

    This method patches time.sleep called from "zeromq.py" file to be noop,
    but calls the real time.sleep otherwise.
    """
    global _orig_time_sleep
    _orig_time_sleep = time.sleep

    def mocked_time_sleep(n):
        global _orig_time_sleep
        if n == 1:
            tb = extract_stack()
            try:
                if tb[-4][0].endswith("zeromq.py"):
                    return
            except IndexError:
                pass
        _orig_time_sleep(n)

    ts = patch("time.sleep").start()
    ts.side_effect = mocked_time_sleep


patch_zeromq_time_sleep()


def clean_database(add_platform_module=True, add_default_arches=True):
    db.session.commit()
    db.drop_all()
    db.create_all()

    if add_default_arches:
        arch_obj = module_build_service.models.ModuleArch(name="x86_64")
        db.session.add(arch_obj)
        db.session.commit()

    if add_platform_module:
        mmd = load_mmd_file(os.path.join(base_dir, "staged_data", "platform.yaml"))
        import_mmd(db.session, mmd)


def init_data(data_size=10, contexts=False, multiple_stream_versions=None, scratch=False):
    """
    Creates data_size * 3 modules in database in different states and
    with different component builds. See _populate_data for more info.

    :param bool contexts: If True, multiple streams and contexts in each stream
        are generated for 'nginx' module.
    :param list/bool multiple_stream_versions: If true, multiple base modules with
        difference stream versions are generated. If set to list, the list defines
        the generated base module streams.
    """
    clean_database()
    if multiple_stream_versions:
        if multiple_stream_versions is True:
            multiple_stream_versions = ["f28.0.0", "f29.0.0", "f29.1.0", "f29.2.0"]
        mmd = load_mmd_file(os.path.join(base_dir, "staged_data", "platform.yaml"))
        for stream in multiple_stream_versions:
            mmd = mmd.copy("platform", stream)

            # Set the virtual_streams based on "fXY" to mark the platform streams
            # with the same major stream_version compatible.
            xmd = mmd.get_xmd()
            xmd["mbs"]["virtual_streams"] = [stream[:3]]
            mmd.set_xmd(xmd)
            import_mmd(db.session, mmd)

            # Just to possibly confuse tests by adding another base module.
            mmd = mmd.copy("bootstrap", stream)
            import_mmd(db.session, mmd)
    with make_session(conf) as session:
        _populate_data(session, data_size, contexts=contexts, scratch=scratch)


def _populate_data(session, data_size=10, contexts=False, scratch=False):
    arch = module_build_service.models.ModuleArch.query.get(1)
    num_contexts = 2 if contexts else 1
    for index in range(data_size):
        for context in range(num_contexts):
            build_one = ModuleBuild(
                name="nginx",
                stream="1",
                version=2 + index,
                state=BUILD_STATES["ready"],
                scratch=scratch,
                modulemd=read_staged_data("nginx_mmd"),
                koji_tag="scrmod-nginx-1.2" if scratch else "module-nginx-1.2",
                scmurl="git://pkgs.domain.local/modules/nginx"
                       "?#ba95886c7a443b36a9ce31abda1f9bef22f2f8c9",
                batch=2,
                # https://www.youtube.com/watch?v=iQGwrK_yDEg,
                owner="Moe Szyslak",
                time_submitted=datetime(2016, 9, 3, 11, 23, 20) + timedelta(minutes=(index * 10)),
                time_modified=datetime(2016, 9, 3, 11, 25, 32) + timedelta(minutes=(index * 10)),
                time_completed=datetime(2016, 9, 3, 11, 25, 32) + timedelta(minutes=(index * 10)),
                rebuild_strategy="changed-and-after",
            )
            build_one.arches.append(arch)

            if contexts:
                build_one.stream = str(index)
                nsvc = "{}:{}:{}:{}".format(
                    build_one.name,
                    build_one.stream,
                    build_one.version,
                    context
                )
                unique_hash = hashlib.sha1(nsvc.encode('utf-8')).hexdigest()
                build_one.build_context = unique_hash
                build_one.runtime_context = unique_hash
                build_one.ref_build_context = unique_hash
                combined_hashes = "{0}:{1}".format(unique_hash, unique_hash)
                build_one.context = hashlib.sha1(combined_hashes.encode("utf-8")).hexdigest()[:8]

            session.add(build_one)
            session.commit()
            build_one_component_release = get_rpm_release(build_one)

            component_one_build_one = ComponentBuild(
                package="nginx",
                scmurl="git://pkgs.domain.local/rpms/nginx?"
                       "#ga95886c8a443b36a9ce31abda1f9bed22f2f8c3",
                format="rpms",
                task_id=12312345 + index,
                state=koji.BUILD_STATES["COMPLETE"],
                nvr="nginx-1.10.1-2.{0}".format(build_one_component_release),
                batch=1,
                module_id=2 + index * 3,
                tagged=True,
                tagged_in_final=True,
            )

            component_two_build_one = ComponentBuild(
                package="module-build-macros",
                scmurl="/tmp/module_build_service-build-macrosWZUPeK/SRPMS/"
                       "module-build-macros-0.1-1.module_nginx_1_2.src.rpm",
                format="rpms",
                task_id=12312321 + index,
                state=koji.BUILD_STATES["COMPLETE"],
                nvr="module-build-macros-01-1.{0}".format(build_one_component_release),
                batch=2,
                module_id=2 + index * 3,
                tagged=True,
                tagged_in_final=True,
            )

        build_two = ModuleBuild(
            name="postgressql",
            stream="1",
            version=2 + index,
            state=BUILD_STATES["done"],
            scratch=scratch,
            modulemd=read_staged_data("testmodule"),
            koji_tag="scrmod-postgressql-1.2" if scratch else "module-postgressql-1.2",
            scmurl="git://pkgs.domain.local/modules/postgressql"
                   "?#aa95886c7a443b36a9ce31abda1f9bef22f2f8c9",
            batch=2,
            owner="some_user",
            time_submitted=datetime(2016, 9, 3, 12, 25, 33) + timedelta(minutes=(index * 10)),
            time_modified=datetime(2016, 9, 3, 12, 27, 19) + timedelta(minutes=(index * 10)),
            time_completed=datetime(2016, 9, 3, 11, 27, 19) + timedelta(minutes=(index * 10)),
            rebuild_strategy="changed-and-after",
        )
        build_two.arches.append(arch)

        session.add(build_two)
        session.commit()
        build_two_component_release = get_rpm_release(build_two)

        component_one_build_two = ComponentBuild(
            package="postgresql",
            scmurl="git://pkgs.domain.local/rpms/postgresql"
                   "?#dc95586c4a443b26a9ce38abda1f9bed22f2f8c3",
            format="rpms",
            task_id=2433433 + index,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="postgresql-9.5.3-4.{0}".format(build_two_component_release),
            batch=2,
            module_id=3 + index * 3,
            tagged=True,
            tagged_in_final=True,
        )

        component_two_build_two = ComponentBuild(
            package="module-build-macros",
            scmurl="/tmp/module_build_service-build-macrosWZUPeK/SRPMS/"
                   "module-build-macros-0.1-1.module_postgresql_1_2.src.rpm",
            format="rpms",
            task_id=47383993 + index,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="module-build-macros-01-1.{0}".format(build_two_component_release),
            batch=1,
            module_id=3 + index * 3,
        )

        build_three = ModuleBuild(
            name="testmodule",
            stream="4.3.43",
            version=6 + index,
            state=BUILD_STATES["wait"],
            scratch=scratch,
            modulemd=read_staged_data("testmodule"),
            koji_tag=None,
            scmurl="git://pkgs.domain.local/modules/testmodule"
                   "?#ca95886c7a443b36a9ce31abda1f9bef22f2f8c9",
            batch=0,
            owner="some_other_user",
            time_submitted=datetime(2016, 9, 3, 12, 28, 33) + timedelta(minutes=(index * 10)),
            time_modified=datetime(2016, 9, 3, 12, 28, 40) + timedelta(minutes=(index * 10)),
            time_completed=None,
            rebuild_strategy="changed-and-after",
        )
        session.add(build_three)
        session.commit()
        build_three_component_release = get_rpm_release(build_three)

        component_one_build_three = ComponentBuild(
            package="rubygem-rails",
            scmurl="git://pkgs.domain.local/rpms/rubygem-rails"
                   "?#dd55886c4a443b26a9ce38abda1f9bed22f2f8c3",
            format="rpms",
            task_id=2433433 + index,
            state=koji.BUILD_STATES["FAILED"],
            nvr="postgresql-9.5.3-4.{0}".format(build_three_component_release),
            batch=2,
            module_id=4 + index * 3,
        )

        component_two_build_three = ComponentBuild(
            package="module-build-macros",
            scmurl="/tmp/module_build_service-build-macrosWZUPeK/SRPMS/"
                   "module-build-macros-0.1-1.module_testmodule_1_2.src.rpm",
            format="rpms",
            task_id=47383993 + index,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="module-build-macros-01-1.{0}".format(build_three_component_release),
            batch=1,
            module_id=4 + index * 3,
            tagged=True,
            build_time_only=True,
        )

        session.add(component_one_build_one)
        session.add(component_two_build_one)
        session.add(component_one_build_two)
        session.add(component_two_build_two)
        session.add(component_one_build_three)
        session.add(component_two_build_three)
        session.commit()


def scheduler_init_data(tangerine_state=None, scratch=False):
    """ Creates a testmodule in the building state with all the components in the same batch
    """
    clean_database()

    current_dir = os.path.dirname(__file__)
    formatted_testmodule_yml_path = os.path.join(
        current_dir, "staged_data", "formatted_testmodule.yaml")
    mmd = load_mmd_file(formatted_testmodule_yml_path)
    mmd.get_rpm_component("tangerine").set_buildorder(0)

    platform_br = module_build_service.models.ModuleBuild.query.get(1)
    arch = module_build_service.models.ModuleArch.query.get(1)

    module_build = module_build_service.models.ModuleBuild(
        name="testmodule",
        stream="master",
        version=20170109091357,
        state=BUILD_STATES["build"],
        scratch=scratch,
        build_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb0",
        runtime_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb0",
        context="7c29193d",
        koji_tag="scrmod-testmodule-master-20170109091357-7c29193d"
                 if scratch
                 else "module-testmodule-master-20170109091357-7c29193d",
        scmurl="https://src.stg.fedoraproject.org/modules/testmodule.git?#ff1ea79",
        batch=3 if tangerine_state else 2,
        # https://www.youtube.com/watch?v=iOKymYVSaJE
        owner="Buzz Lightyear",
        time_submitted=datetime(2017, 2, 15, 16, 8, 18),
        time_modified=datetime(2017, 2, 15, 16, 19, 35),
        rebuild_strategy="changed-and-after",
        modulemd=mmd_to_str(mmd),
    )

    module_build.arches.append(arch)
    module_build.buildrequires.append(platform_br)
    build_one_component_release = get_rpm_release(module_build)

    module_build.component_builds.extend([
        module_build_service.models.ComponentBuild(
            package="perl-Tangerine",
            scmurl="https://src.fedoraproject.org/rpms/perl-Tangerine"
                   "?#4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            format="rpms",
            task_id=90276227,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="perl-Tangerine-0.23-1.{0}".format(build_one_component_release),
            batch=2,
            ref="4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            tagged=True,
            tagged_in_final=True,
        ),
        module_build_service.models.ComponentBuild(
            package="perl-List-Compare",
            scmurl="https://src.fedoraproject.org/rpms/perl-List-Compare"
                   "?#76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb",
            format="rpms",
            task_id=90276228,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="perl-List-Compare-0.53-5.{0}".format(build_one_component_release),
            batch=2,
            ref="76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb",
            tagged=True,
            tagged_in_final=True,
        ),
        module_build_service.models.ComponentBuild(
            package="tangerine",
            scmurl="https://src.fedoraproject.org/rpms/tangerine"
                   "?#fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            format="rpms",
            batch=3,
            ref="fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            state=tangerine_state,
            task_id=90276315 if tangerine_state else None,
            nvr="tangerine-0.22-3.{}".format(build_one_component_release)
            if tangerine_state
            else None,
            tagged=tangerine_state == koji.BUILD_STATES["COMPLETE"],
            tagged_in_final=tangerine_state == koji.BUILD_STATES["COMPLETE"],
        ),
        module_build_service.models.ComponentBuild(
            package="module-build-macros",
            scmurl="/tmp/module_build_service-build-macrosqr4AWH/SRPMS/module-build-"
                   "macros-0.1-1.module_testmodule_master_20170109091357.src.rpm",
            format="rpms",
            task_id=90276181,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="module-build-macros-0.1-1.{}".format(build_one_component_release),
            batch=1,
            tagged=True,
            build_time_only=True,
        ),
    ])

    with make_session(conf) as session:
        session.add(platform_br)
        session.add(module_build)
        session.commit()


def reuse_component_init_data():
    clean_database()

    current_dir = os.path.dirname(__file__)
    formatted_testmodule_yml_path = os.path.join(
        current_dir, "staged_data", "formatted_testmodule.yaml")
    mmd = load_mmd_file(formatted_testmodule_yml_path)

    platform_br = module_build_service.models.ModuleBuild.query.get(1)
    arch = module_build_service.models.ModuleArch.query.get(1)

    build_one = module_build_service.models.ModuleBuild(
        name="testmodule",
        stream="master",
        version=20170109091357,
        state=BUILD_STATES["ready"],
        ref_build_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb0",
        runtime_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb0",
        build_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb1",
        context="78e4a6fd",
        koji_tag="module-testmodule-master-20170109091357-78e4a6fd",
        scmurl="https://src.stg.fedoraproject.org/modules/testmodule.git?#ff1ea79",
        batch=3,
        owner="Tom Brady",
        time_submitted=datetime(2017, 2, 15, 16, 8, 18),
        time_modified=datetime(2017, 2, 15, 16, 19, 35),
        time_completed=datetime(2017, 2, 15, 16, 19, 35),
        rebuild_strategy="changed-and-after",
    )

    build_one_component_release = get_rpm_release(build_one)

    mmd.set_version(int(build_one.version))
    xmd = mmd.get_xmd()
    xmd["mbs"]["scmurl"] = build_one.scmurl
    xmd["mbs"]["commit"] = "ff1ea79fc952143efeed1851aa0aa006559239ba"
    mmd.set_xmd(xmd)
    build_one.modulemd = mmd_to_str(mmd)
    build_one.arches.append(arch)
    build_one.buildrequires.append(platform_br)

    build_one.component_builds.extend([
        module_build_service.models.ComponentBuild(
            package="perl-Tangerine",
            scmurl="https://src.fedoraproject.org/rpms/perl-Tangerine"
                   "?#4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            format="rpms",
            task_id=90276227,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="perl-Tangerine-0.23-1.{0}".format(build_one_component_release),
            batch=2,
            ref="4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            tagged=True,
            tagged_in_final=True,
        ),
        module_build_service.models.ComponentBuild(
            package="perl-List-Compare",
            scmurl="https://src.fedoraproject.org/rpms/perl-List-Compare"
                   "?#76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb",
            format="rpms",
            task_id=90276228,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="perl-List-Compare-0.53-5.{0}".format(build_one_component_release),
            batch=2,
            ref="76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb",
            tagged=True,
            tagged_in_final=True,
        ),
        module_build_service.models.ComponentBuild(
            package="tangerine",
            scmurl="https://src.fedoraproject.org/rpms/tangerine"
                   "?#fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            format="rpms",
            task_id=90276315,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="tangerine-0.22-3.{0}".format(build_one_component_release),
            batch=3,
            ref="fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            tagged=True,
            tagged_in_final=True,
        ),
        module_build_service.models.ComponentBuild(
            package="module-build-macros",
            scmurl="/tmp/module_build_service-build-macrosqr4AWH/SRPMS/module-build-"
                   "macros-0.1-1.module_testmodule_master_20170109091357.src.rpm",
            format="rpms",
            task_id=90276181,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="module-build-macros-0.1-1.{0}".format(build_one_component_release),
            batch=1,
            tagged=True,
            build_time_only=True,
        ),
    ])

    build_two = module_build_service.models.ModuleBuild(
        name="testmodule",
        stream="master",
        version=20170219191323,
        state=BUILD_STATES["build"],
        ref_build_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb0",
        runtime_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb0",
        build_context="ac4de1c346dcf09ce77d38cd4e75094ec1c08eb1",
        context="c40c156c",
        koji_tag="module-testmodule-master-20170219191323-c40c156c",
        scmurl="https://src.stg.fedoraproject.org/modules/testmodule.git?#55f4a0a",
        batch=1,
        owner="Tom Brady",
        time_submitted=datetime(2017, 2, 19, 16, 8, 18),
        time_modified=datetime(2017, 2, 19, 16, 8, 18),
        rebuild_strategy="changed-and-after",
    )

    build_two_component_release = get_rpm_release(build_two)

    mmd.set_version(int(build_one.version))
    xmd = mmd.get_xmd()
    xmd["mbs"]["scmurl"] = build_one.scmurl
    xmd["mbs"]["commit"] = "55f4a0a2e6cc255c88712a905157ab39315b8fd8"
    mmd.set_xmd(xmd)
    build_two.modulemd = mmd_to_str(mmd)
    build_two.arches.append(arch)
    build_two.buildrequires.append(platform_br)

    build_two.component_builds.extend([
        module_build_service.models.ComponentBuild(
            package="perl-Tangerine",
            scmurl="https://src.fedoraproject.org/rpms/perl-Tangerine"
                   "?#4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            format="rpms",
            batch=2,
            ref="4ceea43add2366d8b8c5a622a2fb563b625b9abf",
        ),
        module_build_service.models.ComponentBuild(
            package="perl-List-Compare",
            scmurl="https://src.fedoraproject.org/rpms/perl-List-Compare"
                   "?#76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb",
            format="rpms",
            batch=2,
            ref="76f9d8c8e87eed0aab91034b01d3d5ff6bd5b4cb",
        ),
        module_build_service.models.ComponentBuild(
            package="tangerine",
            scmurl="https://src.fedoraproject.org/rpms/tangerine"
                   "?#fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            format="rpms",
            batch=3,
            ref="fbed359411a1baa08d4a88e0d12d426fbf8f602c",
        ),
        module_build_service.models.ComponentBuild(
            package="module-build-macros",
            scmurl="/tmp/module_build_service-build-macrosqr4AWH/SRPMS/module-build-"
                   "macros-0.1-1.module_testmodule_master_20170219191323.src.rpm",
            format="rpms",
            task_id=90276186,
            state=koji.BUILD_STATES["COMPLETE"],
            nvr="module-build-macros-0.1-1.{0}".format(build_two_component_release),
            batch=1,
            tagged=True,
            build_time_only=True,
        ),
    ])

    with make_session(conf) as session:
        session.add(platform_br)
        session.add(build_one)
        session.add(build_two)
        session.commit()


def reuse_shared_userspace_init_data():
    clean_database()

    with make_session(conf) as session:
        # Create shared-userspace-570, state is COMPLETE, all components
        # are properly built.
        current_dir = os.path.dirname(__file__)
        formatted_testmodule_yml_path = os.path.join(
            current_dir, "staged_data", "shared-userspace-570.yaml")
        mmd = load_mmd_file(formatted_testmodule_yml_path)

        module_build = module_build_service.models.ModuleBuild(
            name=mmd.get_module_name(),
            stream=mmd.get_stream_name(),
            version=mmd.get_version(),
            build_context="e046b867a400a06a3571f3c71142d497895fefbe",
            runtime_context="50dd3eb5dde600d072e45d4120e1548ce66bc94a",
            state=BUILD_STATES["ready"],
            modulemd=mmd_to_str(mmd),
            koji_tag="module-shared-userspace-f26-20170601141014-75f92abb",
            scmurl="https://src.stg.fedoraproject.org/modules/testmodule.git?#7fea453",
            batch=16,
            owner="Tom Brady",
            time_submitted=datetime(2017, 2, 15, 16, 8, 18),
            time_modified=datetime(2017, 2, 15, 16, 19, 35),
            time_completed=datetime(2017, 2, 15, 16, 19, 35),
            rebuild_strategy="changed-and-after",
        )

        components = [
            mmd.get_rpm_component(rpm)
            for rpm in mmd.get_rpm_component_names()
        ]
        components.sort(key=lambda x: x.get_buildorder())
        previous_buildorder = None
        batch = 1
        for pkg in components:
            # Increment the batch number when buildorder increases.
            if previous_buildorder != pkg.get_buildorder():
                previous_buildorder = pkg.get_buildorder()
                batch += 1

            pkgref = mmd.get_xmd()["mbs"]["rpms"][pkg.get_name()]["ref"]
            full_url = pkg.get_repository() + "?#" + pkgref

            module_build.component_builds.append(
                module_build_service.models.ComponentBuild(
                    package=pkg.get_name(),
                    format="rpms",
                    scmurl=full_url,
                    batch=batch,
                    ref=pkgref,
                    state=1,
                    tagged=True,
                    tagged_in_final=True,
                )
            )

        session.add(module_build)
        session.commit()

        # Create shared-userspace-577, state is WAIT, no component built
        formatted_testmodule_yml_path = os.path.join(
            current_dir, "staged_data", "shared-userspace-577.yaml"
        )
        mmd2 = load_mmd_file(formatted_testmodule_yml_path)

        module_build = module_build_service.models.ModuleBuild(
            name=mmd2.get_module_name(),
            stream=mmd2.get_stream_name(),
            version=mmd2.get_version(),
            build_context="e046b867a400a06a3571f3c71142d497895fefbe",
            runtime_context="50dd3eb5dde600d072e45d4120e1548ce66bc94a",
            state=BUILD_STATES["done"],
            modulemd=mmd_to_str(mmd2),
            koji_tag="module-shared-userspace-f26-20170605091544-75f92abb",
            scmurl="https://src.stg.fedoraproject.org/modules/testmodule.git?#7fea453",
            batch=0,
            owner="Tom Brady",
            time_submitted=datetime(2017, 2, 15, 16, 8, 18),
            time_modified=datetime(2017, 2, 15, 16, 19, 35),
            time_completed=datetime(2017, 2, 15, 16, 19, 35),
            rebuild_strategy="changed-and-after",
        )

        components2 = [
            mmd2.get_rpm_component(rpm)
            for rpm in mmd2.get_rpm_component_names()
        ]
        # Store components to database in different order than for 570 to
        # reproduce the reusing issue.
        components2.sort(key=lambda x: len(x.get_name()))
        components2.sort(key=lambda x: x.get_buildorder())
        previous_buildorder = None
        batch = 1
        for pkg in components2:
            # Increment the batch number when buildorder increases.
            if previous_buildorder != pkg.get_buildorder():
                previous_buildorder = pkg.get_buildorder()
                batch += 1

            pkgref = mmd2.get_xmd()["mbs"]["rpms"][pkg.get_name()]["ref"]
            full_url = pkg.get_repository() + "?#" + pkgref

            module_build.component_builds.append(
                module_build_service.models.ComponentBuild(
                    package=pkg.get_name(), format="rpms", scmurl=full_url, batch=batch, ref=pkgref)
            )

        session.add(module_build)
        session.commit()


def make_module(
    nsvc,
    requires_list=None,
    build_requires_list=None,
    base_module=None,
    filtered_rpms=None,
    xmd=None,
    store_to_db=True,
    virtual_streams=None,
    arches=None,
):
    """
    Creates new models.ModuleBuild defined by `nsvc` string with requires
    and buildrequires set according to ``requires_list`` and ``build_requires_list``.

    :param str nsvc: name:stream:version:context of a module.
    :param list_of_dicts requires_list: List of dictionaries defining the
        requires in the mmd requires field format.
    :param list_of_dicts build_requires_list: List of dictionaries defining the
        build_requires_list in the mmd build_requires_list field format.
    :param filtered_rpms: list of filtered RPMs which are added to filter
        section in module metadata.
    :type filtered_rpms: list[str]
    :param dict xmd: a mapping representing XMD section in module metadata. A
        custom xmd could be passed for testing a particular scenario and some
        default key/value pairs are added if not present.
    :param bool store_to_db: whether to store created module metadata to the
        database.
    :param list virtual_streams: List of virtual streams provided by this module.
    :param list arches: List of architectures this module is built against.
        If set to None, ["x86_64"] is used as a default.
    :return: New Module Build if set to store module metadata to database,
        otherwise the module metadata is returned.
    :rtype: ModuleBuild or Modulemd.Module
    """
    name, stream, version, context = nsvc.split(":")
    mmd = Modulemd.ModuleStreamV2.new(name, stream)
    mmd.set_version(int(version))
    mmd.set_context(context)
    mmd.set_summary("foo")
    # Test unicode in mmd.
    mmd.set_description(u"foo \u2019s")
    mmd.add_module_license("GPL")

    if filtered_rpms:
        for rpm in filtered_rpms:
            mmd.add_rpm_filter(rpm)

    if requires_list is not None and build_requires_list is not None:
        if not isinstance(requires_list, list):
            requires_list = [requires_list]
        if not isinstance(build_requires_list, list):
            build_requires_list = [build_requires_list]

        for requires, build_requires in zip(requires_list, build_requires_list):
            deps = Modulemd.Dependencies()
            for req_name, req_streams in requires.items():
                if req_streams == []:
                    deps.set_empty_runtime_dependencies_for_module(req_name)
                else:
                    for req_stream in req_streams:
                        deps.add_runtime_stream(req_name, req_stream)

            for req_name, req_streams in build_requires.items():
                if req_streams == []:
                    deps.set_empty_buildtime_dependencies_for_module(req_name)
                else:
                    for req_stream in req_streams:
                        deps.add_buildtime_stream(req_name, req_stream)

            mmd.add_dependencies(deps)

    # Caller could pass whole xmd including mbs, but if something is missing,
    # default values are given here.
    xmd = xmd or {"mbs": {}}
    xmd_mbs = xmd["mbs"]
    if "buildrequires" not in xmd_mbs:
        xmd_mbs["buildrequires"] = {}
    if "requires" not in xmd_mbs:
        xmd_mbs["requires"] = {}
    if "commit" not in xmd_mbs:
        xmd_mbs["commit"] = "ref_%s" % context
    if "mse" not in xmd_mbs:
        xmd_mbs["mse"] = "true"

    if virtual_streams:
        xmd_mbs["virtual_streams"] = virtual_streams

    mmd.set_xmd(xmd)

    if not store_to_db:
        return mmd

    module_build = ModuleBuild(
        name=name,
        stream=stream,
        stream_version=ModuleBuild.get_stream_version(stream),
        version=version,
        context=context,
        state=BUILD_STATES["ready"],
        scmurl="https://src.stg.fedoraproject.org/modules/unused.git?#ff1ea79",
        batch=1,
        owner="Tom Brady",
        time_submitted=datetime(2017, 2, 15, 16, 8, 18),
        time_modified=datetime(2017, 2, 15, 16, 19, 35),
        rebuild_strategy="changed-and-after",
        build_context=context,
        runtime_context=context,
        modulemd=mmd_to_str(mmd),
        koji_tag=xmd["mbs"]["koji_tag"] if "koji_tag" in xmd["mbs"] else None,
    )
    if base_module:
        module_build.buildrequires.append(base_module)
    db.session.add(module_build)
    db.session.commit()

    if virtual_streams:
        for virtual_stream in virtual_streams:
            vs_obj = db.session.query(VirtualStream).filter_by(name=virtual_stream).first()
            if not vs_obj:
                vs_obj = VirtualStream(name=virtual_stream)
                db.session.add(vs_obj)
                db.session.commit()

            if vs_obj not in module_build.virtual_streams:
                module_build.virtual_streams.append(vs_obj)
                db.session.commit()

    if arches is None:
        arches = ["x86_64"]
    for arch in arches:
        arch_obj = db.session.query(module_build_service.models.ModuleArch).filter_by(
            name=arch).first()
        if not arch_obj:
            arch_obj = module_build_service.models.ModuleArch(name=arch)
            db.session.add(arch_obj)
            db.session.commit()

        if arch_obj not in module_build.arches:
            module_build.arches.append(arch_obj)
            db.session.commit()

    return module_build
