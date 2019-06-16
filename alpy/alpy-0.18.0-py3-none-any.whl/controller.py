# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import logging

import docker

import alpy.console
import alpy.node
import alpy.utils


class TestEnvironment:
    def __init__(self):
        self.exit_stack = contextlib.ExitStack()

    @contextlib.contextmanager
    def enter(self):
        logger = logging.getLogger(__name__)
        with self.exit_stack:
            try:
                yield
            except:
                logger.error("Test failed")
                raise
            self.exit_stack = self.exit_stack.pop_all()
        logger.info("Enter test environment")

    def close_after_failure(self):
        logger = logging.getLogger(__name__)
        logger.error("Exit test environment with failure")
        try:
            self.exit_stack.close()
        finally:
            logger.error("Test failed")

    def close_after_success(self):
        logger = logging.getLogger(__name__)
        logger.info("Exit test environment with success")
        try:
            self.exit_stack.close()
        except:
            logger.error("Test failed")
            raise
        logger.info("Test passed")


def tap_interfaces(link_count):
    return [f"alpy{i}" for i in range(link_count)]


class ControllerBase:
    def __init__(self, *, link_count, timeout, test_name, test_description):
        alpy.utils.configure_logging()
        self._link_count = link_count
        self.timeout = timeout
        self._skeleton = None
        self.docker_client = None
        self.qmp = None
        self.console = None
        self._test_environment = TestEnvironment()
        logger = logging.getLogger(__name__)
        logger.info("Test name: " + test_name)
        logger.info("Test description: " + test_description)

    def __enter__(self):
        with self._test_environment.enter():
            self._create()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._test_environment.close_after_failure()
        else:
            self._test_environment.close_after_success()

    def configure_interface(self, *, node, address, gateway=None):
        alpy.container.configure_interface(
            f"node{node}",
            address,
            gateway,
            docker_client=self.docker_client,
            image="busybox:latest",
            timeout=self.timeout,
        )

    def _create(self):
        self.docker_client = docker.from_env()
        self._test_environment.exit_stack.callback(self.docker_client.close)

        self._skeleton = alpy.node.Skeleton(
            tap_interfaces=tap_interfaces(self._link_count),
            docker_client=self.docker_client,
            timeout=self.timeout,
            busybox_image="busybox:latest",
            iproute2_image="debian:testing",
        )

        self._test_environment.exit_stack.callback(self._skeleton.close)
        self._skeleton.create_tap_interfaces()
        qemu_args = self._get_qemu_args()

        self.qmp = self._test_environment.exit_stack.enter_context(
            alpy.qemu.run(qemu_args, self.timeout)
        )

        self._skeleton.create()

        self.console = self._test_environment.exit_stack.enter_context(
            alpy.console.connect(timeout=self.timeout)
        )
        alpy.qemu.read_events(self.qmp)

    def _get_qemu_args(self):
        raise NotImplementedError
