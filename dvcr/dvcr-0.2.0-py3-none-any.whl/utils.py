import logging
import random

import colorama
import docker

COLORS = [
    colorama.Fore.RED,
    colorama.Fore.GREEN,
    colorama.Fore.YELLOW,
    colorama.Fore.BLUE,
    colorama.Fore.MAGENTA,
    colorama.Fore.CYAN,
]

colorama.init(autoreset=True)


def wait(target, port, network, logger):

    logger.info("Waiting for %s ⏳", bright(target))

    client = docker.from_env()

    waiter = client.containers.run(
        image="ubuntu:14.04",
        detach=True,
        name="wait_for_" + target,
        network=network.name,
        command=[
            "/bin/bash",
            "-c",
            """
            while ! nc -z {target} {port};
            do
                sleep 5;
            done;
            """.format(
                target=target, port=port
            ),
        ],
    )

    waiter.wait()

    logger.info("%s is up! 🚀", bright(target))

    waiter.stop()
    waiter.remove()


def init_logger(name):

    color = random.choice(COLORS)
    COLORS.remove(color)

    logger = logging.getLogger(name="dvcr_" + name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        color + "[" + name + "]" + colorama.Fore.RESET + ": %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def bright(string):
    return colorama.Style.BRIGHT + string + colorama.Style.NORMAL
