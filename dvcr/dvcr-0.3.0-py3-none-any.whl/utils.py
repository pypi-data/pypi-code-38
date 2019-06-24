import logging
import random

import colorama
import docker

COLOR = [
    colorama.Fore.RED,
    colorama.Fore.GREEN,
    colorama.Fore.YELLOW,
    colorama.Fore.BLUE,
    colorama.Fore.MAGENTA,
    colorama.Fore.CYAN,
    colorama.Fore.LIGHTRED_EX,
    colorama.Fore.LIGHTGREEN_EX,
    colorama.Fore.LIGHTYELLOW_EX,
    colorama.Fore.LIGHTBLUE_EX,
    colorama.Fore.LIGHTMAGENTA_EX,
    colorama.Fore.LIGHTCYAN_EX,
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


def init_logger(name: str, level: int = logging.INFO):

    logger_name = "dvcr_" + name

    if logger_name in logging.root.manager.loggerDict:
        return logging.getLogger(name=logger_name)   # Return logger immediately if it already exists

    logger = logging.getLogger(name=logger_name)

    try:
        color = random.choice(COLOR)
        COLOR.remove(color)
    except IndexError:
        color = colorama.Fore.WHITE

    logger.setLevel(level=level)

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
            color + "[" + name + "]" + colorama.Fore.RESET + ": %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def bright(string):
    return colorama.Style.BRIGHT + string + colorama.Style.NORMAL
