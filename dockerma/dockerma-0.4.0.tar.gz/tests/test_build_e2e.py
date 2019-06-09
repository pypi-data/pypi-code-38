#!/usr/bin/env python
# -*- coding: utf-8

import subprocess
import tempfile
import textwrap

import pytest
import sys


class TestBuildE2E(object):
    @pytest.fixture(scope="session")
    def image_name(self):
        vi = sys.version_info
        return "dockerma-test-{}{}".format(vi.major, vi.minor)

    @pytest.fixture
    def dockerfile(self):
        with tempfile.NamedTemporaryFile("w", prefix="Dockerfile-build-e2e-", delete=False) as tfile:
            tfile.write(textwrap.dedent("""\
                # dockerma archs:arm,amd64,arm64:
                FROM redis:5.0.4-alpine3.9 as base
                
                COPY ./README.rst /
                
                FROM base as second
                
                FROM traefik:v1.7.11-alpine as final
                
                COPY --from=base /README.rst /
                
                RUN apk update
                """))
            tfile.flush()
            yield tfile.name

    @pytest.fixture
    def images(self, image_name):
        def _clean():
            for version in ("v1.0", "latest"):
                for arch in ("arm", "arm64", "amd64"):
                    tag = "{}:{}-{}".format(image_name, version, arch)
                    subprocess.check_output(["docker", "rmi", "--force", tag], stderr=subprocess.STDOUT)

        _clean()
        yield
        _clean()

    @pytest.mark.usefixtures("images")
    def test_build(self, dockerfile, image_name):
        subprocess.check_call(["dockerma", "--log-level", "debug", "--debug",
                               "build",
                               "-t", "{}:v1.0".format(image_name),
                               "-t", "{}:latest".format(image_name),
                               "-f", dockerfile,
                               "."])
        output = subprocess.check_output(["docker", "images", image_name], universal_newlines=True)
        lines = output.splitlines()
        assert len(lines) == 7
        for version in ("v1.0", "latest"):
            for arch in ("arm", "arm64", "amd64"):
                tag = "{}-{}".format(version, arch)
                assert tag in output
