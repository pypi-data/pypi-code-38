import os
import configparser
import time

if not os.path.exists('%s/.snw' % os.getenv('HOME')):
    os.mkdir('%s/.snw' % os.getenv('HOME'))


def _credential_file(url):
    norm_url = url.strip("/")
    p = norm_url.rfind("://")
    if p:
        norm_url = norm_url[p+3:]
    norm_url = norm_url.replace("/", "_")
    return '%s/.snw/credential-%s' % (os.getenv('HOME'), norm_url)


def get_credential(url, account=None):
    credential_file = _credential_file(url)
    config = configparser.ConfigParser()
    if os.path.exists(credential_file):
        config.read_file(open(credential_file))
    if not account:
        for section in config:
            if config[section].get("current"):
                account = section
                break
    if account in config:
        if config[account]["time"]+config[account]["duration"] >= time.time():
            return config[account]["token"], account
    return None, account


def set_credential(url, account, token, duration, time):
    credential_file = _credential_file(url)
    config = configparser.ConfigParser()
    if os.path.exists(credential_file):
        config.read_file(open(credential_file))
    for section in config:
        config.remove_option(section, "current")
    config[account] = {"token": token, "duration": duration, "time": time, "current": "True"}
    with open(credential_file, "w") as fh:
        config.write(fh)


def activate_credential(url, account):
    credential_file = _credential_file(url)
    config = configparser.ConfigParser()
    if os.path.exists(credential_file):
        config.read_file(open(credential_file))
    for section in config:
        config.remove_option(section, "current")
    config[account]["current"] = "True"
    with open(credential_file, "w") as fh:
        config.write(fh)


def remove_credential(url, account):
    credential_file = _credential_file(url)
    config = configparser.ConfigParser()
    if os.path.exists(credential_file):
        config.read_file(open(credential_file))
    if config.remove_section(account):
        with open(credential_file, "w") as fh:
            config.write(fh)


if __name__ == "__main__":
    set_credential("http://snw-api.net", "senellart@systran.fr", "1234")
