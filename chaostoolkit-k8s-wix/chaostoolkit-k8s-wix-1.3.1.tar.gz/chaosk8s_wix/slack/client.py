# -*- coding: utf-8 -*-

from logzero import logger
from slackclient import SlackClient
from chaoslib.settings import load_settings
import os
import socket


__all__ = ["post_message", "get_val_from_env"]


def get_job_url():
    """
    Gets Jenkins job url from JOB_URL env var
    :return: value JOB_URL, if defined, local hostname otherwise
    """
    retval = socket.gethostname()
    val = os.getenv("BUILD_URL")
    if val is not None:
        retval = val
    return retval


def get_val_from_env(entry, key_name, envvar_name) -> str:
    """
    Return value from settings entry token. Env variable SLACK_TOKEN and SLACK_CHANNEL will have precedence before any
    other configurations
    :param entry: current entry with slack configuration from ~/.chaostoolkit/settings.yml
    :param key_name: name of key in entry that holds default value
    :param envvar_name: name of env var that holds value
    :return: if  defined, the value of env var . token from entry otherwise
    """
    value = ""
    if entry is not None:
        value = entry[key_name]
    val = os.getenv(envvar_name)
    if val is not None:
        value = val
    return value


def get_settings():
    """
    Gets relevant settings for slack notifications
    :return: dictionary with token and channel for slack notifications
    """
    retval = {}
    retval["token"] = get_val_from_env(None, "token", "SLACK_TOKEN")
    retval["channel"] = get_val_from_env(None, "token", "SLACK_CHANNEL")

    return retval


def post_message(message_text: str = " "):
    """
    Post message to channel defined in chaostoolkit settings file (~/.chaostoolkit/settings.yaml)
    :param message_text: Message text to send
    :return: 0 if everything is ok , error code otherwise
    """

    retval = 1
    settings = get_settings()
    if settings is not None and len(settings.keys()) > 0 and "token" in settings.keys():
        retval = 1
        token = settings["token"]
        token = token.strip()
        channel = settings["channel"]
        channel = "#{c}".format(c=channel.lstrip("#").strip())

        sc = SlackClient(token)
        text_to_send = message_text + '\n at ' + get_job_url()
        result = sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=text_to_send,
        )

        if result.get("ok", False) is False:
            print("Sending slack message '{}' failed".format(message_text))
            retval = 1
        else:
            retval = 0
    return retval
