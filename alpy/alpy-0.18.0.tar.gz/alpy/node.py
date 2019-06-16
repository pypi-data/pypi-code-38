# SPDX-License-Identifier: GPL-3.0-or-later

import alpy.container
import alpy.utils


class NodeTap:
    def __init__(
        self,
        *,
        docker_client,
        node_container_name,
        interface_name,
        timeout,
        busybox_image,
        iproute2_image,
    ):
        self._docker_client = docker_client
        self._join_node_ns = "container:" + node_container_name
        self._interface_name = interface_name
        self._timeout = timeout
        self._busybox_image = busybox_image
        self._iproute2_image = iproute2_image
        self._interface_in_host_namespace = False

    def create_tap_interface(self):
        self._create_interface()
        self._interface_in_host_namespace = True

    def setup_tap_interface(self):
        self._move_interface_to_node_container()
        self._interface_in_host_namespace = False
        self._rename_interface()
        self._raise_interface()

    def close(self):
        if self._interface_in_host_namespace:
            self._remove_interface()

    def _run_in_container(self, image, command, **kwargs):
        container = self._docker_client.containers.create(
            image, command, **kwargs
        )
        alpy.container.run(container, self._timeout)

    def _create_interface(self):

        self._run_in_container(
            self._iproute2_image,
            ["ip", "tuntap", "add", "mode", "tap", "dev", self._interface_name],
            network_mode="host",
            cap_add=["NET_ADMIN"],
            devices=["/dev/net/tun"],
        )

    def _move_interface_to_node_container(self):

        self._run_in_container(
            self._iproute2_image,
            ["ip", "link", "set", "netns", "1", "dev", self._interface_name],
            network_mode="host",
            pid_mode=self._join_node_ns,
            cap_add=["NET_ADMIN"],
        )

    def _rename_interface(self):

        self._run_in_container(
            self._busybox_image,
            ["ip", "link", "set", "name", "eth0", "dev", self._interface_name],
            network_mode=self._join_node_ns,
            cap_add=["NET_ADMIN"],
        )

    def _raise_interface(self):

        self._run_in_container(
            self._busybox_image,
            ["ip", "link", "set", "up", "dev", "eth0"],
            network_mode=self._join_node_ns,
            cap_add=["NET_ADMIN"],
        )

    def _remove_interface(self):

        self._run_in_container(
            self._busybox_image,
            ["ip", "link", "delete", "dev", self._interface_name],
            network_mode="host",
            cap_add=["NET_ADMIN"],
        )


class NodeContainer:
    def __init__(self, *, docker_client, name, timeout, image):
        self._docker_client = docker_client
        self._name = name
        self._timeout = timeout
        self._image = image
        self._container = None
        self._started = False

    def run(self):

        self._container = self._docker_client.containers.create(
            self._image,
            ["cat"],
            name=self._name,
            network_mode="none",
            stdin_open=True,
        )

        self._container.start()
        alpy.container.wait_running(self._container, self._timeout)
        self._started = True

    def close(self):
        if self._container:
            if self._started:
                self._container.kill()
                self._container.wait(timeout=self._timeout)
            alpy.container.write_logs(self._container)
            self._container.remove()


class Node:
    def __init__(
        self,
        *,
        interface_name,
        node_container_name,
        docker_client,
        timeout,
        busybox_image,
        iproute2_image,
    ):
        self._container = NodeContainer(
            docker_client=docker_client,
            name=node_container_name,
            timeout=timeout,
            image=busybox_image,
        )
        self._tap = NodeTap(
            docker_client=docker_client,
            node_container_name=node_container_name,
            interface_name=interface_name,
            timeout=timeout,
            busybox_image=busybox_image,
            iproute2_image=iproute2_image,
        )

    def create_tap_interface(self):
        self._tap.create_tap_interface()

    def create(self):

        self._container.run()
        self._tap.setup_tap_interface()

    def close(self):
        self._container.close()
        self._tap.close()


class Skeleton:
    def __init__(
        self,
        *,
        tap_interfaces,
        docker_client,
        timeout,
        busybox_image,
        iproute2_image,
    ):
        self._nodes = []
        for node_index, interface_name in enumerate(tap_interfaces):
            node = Node(
                interface_name=interface_name,
                node_container_name=f"node{node_index}",
                docker_client=docker_client,
                timeout=timeout,
                busybox_image=busybox_image,
                iproute2_image=iproute2_image,
            )
            self._nodes.append(node)

    def create_tap_interfaces(self):
        log = alpy.utils.context_logger(__name__)
        with log("Create tap interfaces"):
            for node in self._nodes:
                node.create_tap_interface()

    def create(self):
        log = alpy.utils.context_logger(__name__)
        with log("Create nodes"):
            for node in self._nodes:
                node.create()

    def close(self):
        for node in self._nodes:
            node.close()
