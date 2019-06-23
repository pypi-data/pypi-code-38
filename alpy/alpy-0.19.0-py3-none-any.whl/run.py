# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib

import alpy.node
import alpy.qemu


@contextlib.contextmanager
def qemu_with_skeleton(
    *,
    busybox_image,
    docker_client,
    iproute2_image,
    tap_interfaces,
    timeout,
    qemu_args,
):
    skeleton = alpy.node.Skeleton(
        tap_interfaces=tap_interfaces,
        docker_client=docker_client,
        timeout=timeout,
        busybox_image=busybox_image,
        iproute2_image=iproute2_image,
    )
    try:
        skeleton.create_tap_interfaces()
        with alpy.qemu.run(qemu_args, timeout) as qmp:
            skeleton.create()
            alpy.qemu.read_events(qmp)
            yield qmp
    finally:
        skeleton.close()
