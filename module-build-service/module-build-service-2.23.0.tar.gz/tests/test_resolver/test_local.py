# Copyright (c) 2019  Red Hat, Inc.
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
# Written by Jan Kaluza <jkaluza@redhat.com>

import os
from datetime import datetime

import module_build_service.resolver as mbs_resolver
from module_build_service import db
from module_build_service.utils.general import import_mmd, load_mmd_file, mmd_to_str
from module_build_service.models import ModuleBuild
import tests


base_dir = os.path.join(os.path.dirname(__file__), "..")


class TestLocalResolverModule:
    def setup_method(self):
        tests.reuse_component_init_data()

    def test_get_buildrequired_modulemds(self):
        mmd = load_mmd_file(os.path.join(base_dir, "staged_data", "platform.yaml"))
        mmd = mmd.copy(mmd.get_module_name(), "f8")
        import_mmd(db.session, mmd)
        platform_f8 = ModuleBuild.query.filter_by(stream="f8").one()
        mmd = mmd.copy("testmodule", "master")
        mmd.set_version(20170109091357)
        mmd.set_context("123")
        build = ModuleBuild(
            name="testmodule",
            stream="master",
            version=20170109091357,
            state=5,
            build_context="dd4de1c346dcf09ce77d38cd4e75094ec1c08ec3",
            runtime_context="ec4de1c346dcf09ce77d38cd4e75094ec1c08ef7",
            context="7c29193d",
            koji_tag="module-testmodule-master-20170109091357-7c29193d",
            scmurl="https://src.stg.fedoraproject.org/modules/testmodule.git?#ff1ea79",
            batch=3,
            owner="Dr. Pepper",
            time_submitted=datetime(2018, 11, 15, 16, 8, 18),
            time_modified=datetime(2018, 11, 15, 16, 19, 35),
            rebuild_strategy="changed-and-after",
            modulemd=mmd_to_str(mmd),
        )
        db.session.add(build)
        db.session.commit()

        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="local")
        result = resolver.get_buildrequired_modulemds(
            "testmodule", "master", platform_f8.mmd().get_nsvc())
        nsvcs = set([m.get_nsvc() for m in result])
        assert nsvcs == set(
            ["testmodule:master:20170109091357:9c690d0e", "testmodule:master:20170109091357:123"])
