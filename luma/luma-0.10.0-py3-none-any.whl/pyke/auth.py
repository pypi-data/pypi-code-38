"""
    The auth class is resposible for storing, reading and updating tokens and config settings.
    The CLI should cache tokens until a new one is required. If that's the case the auth class
    retrieves the config variables so a new token can be requested from the platform. Upon success
    the new token is cached and used for subsequent commandsself.
"""

from functools import wraps
from pathlib import Path
from pyparsing import *
import dateutil.parser
import click
import copy
import json
import os


class auth:

  def get_profile(config_data, name):
    return config_data['profiles'].get(name)

  def get_env(config_data, name):
    return config_data['envs'].get(name)

  def set_cache(data):
    clean_data = auth.sanatize_data(data)
    with open(auth.get_cache_file(), 'w+') as outfile:
      json.dump(data, outfile, indent=4, sort_keys=True)

  def clear_cache():
    with open(auth.get_cache_file(), 'w+') as outfile:
      json.dump({}, outfile, indent=4, sort_keys=True)

  def set_cache_token(token):
    cache = auth.load_cache()
    cache['accessToken'] = token
    auth.set_cache(cache)

    return cache

  def get_profile_names(ctx, args, incomplete):
    config = auth.load_config()
    names = config['profiles'].keys()
    return [k for k in names if incomplete in k]

  """
    Data coming from the config file and cache sometimes have extra whitespace
    appended to the values. Their are casses where, values being read with
    extra whitespace are then being written back to the config.
    Track this down and prevent this from happening.
  """
  def sanatize_data(data):
    skip = ['orgName', 'env', 'envName']
    return { k:v.replace(" ", "") if isinstance(v, str) and k not in skip else v for k,v in data.items() }

  def set_profile_token(profile, token):
    config_data = auth.load_config()
    config_data['profiles'][profile]['accessToken'] = token
    auth.save_config(config_data)

    return config_data

  def get_cache_file():
    cache_path = str(Path.home()) + '/.luma_cache'
    if not os.path.exists(cache_path):
      with open(cache_path, 'w+') as cache:
        json.dump({}, cache)

    return cache_path

  def load_cache():
    with open(auth.get_cache_file()) as json_file:
      data = json.load(json_file)

    return data

  def save_config(data):
    for k in data['envs'].keys():
      data['envs'][k] = auth.sanatize_data(data['envs'][k])

    with open(auth.get_config_file(), 'w+') as outfile:
      json.dump(data, outfile, indent=4, sort_keys=True)

  def load_config():
    config_path = auth.get_config_file()
    try:
      with open(config_path) as json_file:
        data = json.load(json_file)
      return data
    except Exception as e:
      raise click.ClickException(click.style('Bad config file found. Please manually fix your congif. Path: {}'.format(config_path), fg='red'))

  def get_config_file():
    config_path = str(Path.home()) + '/.luma_cli_config'
    if not os.path.exists(config_path):
      with open(config_path, 'w') as config:
        json.dump({ "envs": {}, "profiles": {} }, config)

    return config_path

  """
      This decorator should be used on any command that requires company context.
      It ensures that the user runs the command with a valid profile and that the
      profile is able to obtain a token with the correct company context.
  """
  def profile_context_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
      try:
        profile = kwargs.get('profile')
        config_data = auth.load_config()
        profile_data = auth.get_profile(config_data, profile)

        if profile_data is None:
          raise click.BadParameter(click.style('You must provide the name of a profile that you have configured', fg='red'))
        if profile_data.get('orgId') is None or profile_data.get('orgId') == '':
          raise click.BadParameter(click.style('You must finish configuring this profile before you can use it', fg='red'))

        clean_data = auth.sanatize_data(profile_data)

        clean_data['profileName'] = profile
        env_data = auth.sanatize_data(auth.get_env(config_data, clean_data.get('env')))

        cache_data = {**clean_data, **env_data}

        # Protect against error state where 'accessToken' would become null
        if cache_data.get("accessToken") is None:
          cache_data['accessToken'] = " "

        auth.set_cache(cache_data)

      except Exception as e:
        click.echo(click.style(str(e), fg='red'))
        raise click.Abort()

      f(*args, **kwargs)
      auth.clear_cache()

      return
    return decorated_func
