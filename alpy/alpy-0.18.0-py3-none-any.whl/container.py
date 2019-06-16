# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import time

import alpy.utils


def write_logs(container):

    logger = logging.getLogger(__name__)

    def log_each_line(lines_bytes, prefix):
        if lines_bytes:
            for line in lines_bytes.decode().splitlines():
                logger.debug(prefix + line)

    log_each_line(
        container.logs(stdout=True, stderr=False),
        f"{container.short_id} stdout: ",
    )

    log_each_line(
        container.logs(stdout=False, stderr=True),
        f"{container.short_id} stderr: ",
    )


def get_signal_number_from_status_code(code):
    if code >= 128:
        return code - 128
    return None


def log_status_code(code, name):
    logger = logging.getLogger(__name__)
    signal_number = get_signal_number_from_status_code(code)
    if signal_number:
        signal_name = alpy.utils.signal_name(signal_number)
        logger.debug(f"Container {name} was killed by signal {signal_name}")
    else:
        logger.debug(f"Container {name} exited with code {code}")


def check_status_code(code):
    signal_number = get_signal_number_from_status_code(code)
    if signal_number:
        raise alpy.utils.NonZeroExitCode(
            "Container process was killed by signal "
            + alpy.utils.signal_name(signal_number)
        )
    if code != 0:
        raise alpy.utils.NonZeroExitCode(
            f"Container process exited with non-zero code {code}"
        )


def clean_start(container, remove=True):
    try:
        container.start()
    except:
        if remove:
            container.remove()
        raise


def stop(container, timeout, remove=True):
    try:
        container.stop()
        result = container.wait(timeout=timeout)
    finally:
        write_logs(container)
    status_code = int(result["StatusCode"])
    log_status_code(status_code, container.short_id)
    if remove:
        container.remove()


def close(container, timeout, remove=True):
    try:
        result = container.wait(timeout=timeout)
    except:
        logger = logging.getLogger(__name__)
        logger.error(
            "Timed out waiting for container "
            + container.short_id
            + " to stop by itself"
        )
        stop(container, timeout, remove)
        raise
    write_logs(container)
    status_code = int(result["StatusCode"])
    log_status_code(status_code, container.short_id)
    if remove:
        container.remove()
    check_status_code(status_code)


def run(container, timeout, remove=True):
    clean_start(container, remove)
    close(container, timeout, remove)


class Timeout(Exception):
    pass


def wait_running(container, timeout):

    time_start = time.time()
    while True:
        container.reload()
        if container.status == "running":
            break
        if time.time() > time_start + timeout:
            raise Timeout
        time.sleep(0.5)


def configure_interface(
    container_name, address, gateway=None, *, docker_client, image, timeout
):
    add_ip_address(
        container_name,
        address,
        docker_client=docker_client,
        image=image,
        timeout=timeout,
    )
    if gateway:
        add_default_route(
            container_name,
            gateway,
            docker_client=docker_client,
            image=image,
            timeout=timeout,
        )


def add_ip_address(container_name, address, *, docker_client, image, timeout):
    container = docker_client.containers.create(
        image,
        ["ip", "address", "add", address, "dev", "eth0"],
        network_mode="container:" + container_name,
        cap_add=["NET_ADMIN"],
    )
    run(container, timeout)


def add_default_route(
    container_name, gateway, *, docker_client, image, timeout
):
    container = docker_client.containers.create(
        image,
        ["ip", "route", "add", "default", "via", gateway],
        network_mode="container:" + container_name,
        cap_add=["NET_ADMIN"],
    )
    run(container, timeout)
