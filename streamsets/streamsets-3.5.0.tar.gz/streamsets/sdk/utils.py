# Copyright 2019 StreamSets Inc.

"""Assorted utility functions."""

import base64
import logging
import random
import re
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from time import sleep, time

from inflection import camelize

logger = logging.getLogger(__name__)


def get_random_string(characters, length=8):
    """
    Returns a string of the requested length consisting of random combinations of the given
    sequence of string characters.
    """
    return ''.join(random.choice(characters) for _ in range(length))


def join_url_parts(*parts):
    """
    Join a URL from a list of parts. See http://stackoverflow.com/questions/24814657 for
    examples of why urllib.parse.urljoin is insufficient for what we want to do.
    """
    return '/'.join([piece.strip('/') for piece in parts])


def get_params(parameters, exclusions=None):
    """Get a dictionary of parameters to be passed as requests methods' params argument.

    The typical use of this method is to pass in locals() from a function that wraps a
    REST endpoint. It will then create a dictionary, filtering out any exclusions (e.g.
    path parameters) and unset parameters, and use camelize to convert arguments from
    ``this_style`` to ``thisStyle``.
    """
    return {camelize(arg, uppercase_first_letter=False): value
            for arg, value in parameters.items()
            if value is not None and arg not in exclusions}


class VersionSplit:
    """Util function to hold various parts of a version.

    Args:
        name (:obj:`str`)
        delimiter1 (:obj:`str`)
        version (:obj:`str`)
        delimiter2 (:obj:`str`)
        specifier (:obj:`str`)
    """
    __slots__ = ['name', 'delimiter1', 'version', 'delimiter2', 'specifier']
    def __init__(self, name, delimiter1, version, delimiter2, specifier):
        self.name = name
        self.delimiter1 = delimiter1
        self.version = version
        self.delimiter2 = delimiter2
        self.specifier = specifier

    def __iter__(self):
        for attr in self.__slots__:
            yield getattr(self, attr)


class Version:
    """Maven version string abstraction.

    Use this class to enable correct comparison of Maven versioned projects. For our purposes,
    any version is equivalent to any other version that has the same 4-digit version number (i.e.
    3.0.0.0-SNAPSHOT == 3.0.0.0-RC2 == 3.0.0.0).

    Args:
        version (:obj:`str`) or (:obj:`int`) or (:obj:`float`): Version string (e.g. '2.5.0.0-SNAPSHOT').
    """
    # pylint: disable=protected-access,too-few-public-methods
    def __init__(self, version):
        self._pattern = '(^[a-zA-Z]+)?(-)?([\d.]+)(-)?(\w+)?'
        # name (^[a-zA-Z]+) May or may not exist
        # delimiter1 (-)? May or may not exist e.g. - or None
        # version ([\d.]+) Version number e.g. 3.8.2
        # delimiter2 (-)? May or may not exist e.g. - or None
        # specifier (\w*) May or may not exist e.g. RC2

        # Handle the case where version is int or float.
        if isinstance(version, (int, float)):
            version = str(version)

        self._str = version

        groups = re.search(self._pattern, self._str).groups()
        version_split = VersionSplit(*groups)

        # Parse the numeric part of versions.
        numeric_version_list = [int(i) for i in version_split.version.split('.')]

        # Add additional 0's to keep a min length of version. Not so pythonic but, probably is more readable and simple.
        while len(numeric_version_list) < 4:
            numeric_version_list.append(0)

        # Update version_split with appended zeros.
        version_split.version = numeric_version_list

        self._version_split = version_split
        self._tuple = tuple(version_split)

    def __repr__(self):
        return str(self._tuple)

    def __eq__(self, other):
        return (self._version_split.name == other._version_split.name and
                self._version_split.version == other._version_split.version)

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise TypeError('Comparison can only be done for two Version instances.')
        if self._version_split.name != other._version_split.name:
            raise TypeError('Comparison can only be done between two Version instances with same name.')
        return self._version_split.version < other._version_split.version

    def __gt__(self, other):
        return other.__lt__(self)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return other.__ge__(self)


def sdc_value_reader(value):
    """Helper function which can parse SDC Record value (Record JSON in dict format for example)
    and convert to SDC implied Python collection with necessary types being converted from SDC
    to Python.

    Args:
        value: SDC Record value.

    Returns:
        The value.
    """
    # Note: check instance of OrderedDict before dict to avoid superfluous
    # check of OrderedDict getting evaluated for dict
    type_to_function_map = {"LIST_MAP": lambda x: sdc_value_reader(OrderedDict([(key, x[key])
                                                                                for key in range(len(x))])),
                            "LIST": lambda x: sdc_value_reader(x),
                            "MAP": lambda x: sdc_value_reader(x),
                            "SHORT": lambda x: int(x),
                            "INTEGER": lambda x: int(x),
                            "LONG": lambda x: int(x),
                            "CHAR": lambda x: x,
                            "STRING": lambda x: x,
                            "DATE": lambda x: datetime.utcfromtimestamp(x/1000),
                            "DATETIME": lambda x: datetime.utcfromtimestamp(x/1000),
                            "TIME": lambda x: datetime.utcfromtimestamp(x/1000),
                            "BOOLEAN": lambda x: x,
                            "BYTE": lambda x: str(x).encode(),
                            "DOUBLE": lambda x: float(x),
                            "FLOAT" : lambda x: float(x),
                            "DECIMAL": lambda x: Decimal(str(x)),
                            "BYTE_ARRAY": lambda x: base64.b64decode(x)}
    if isinstance(value, OrderedDict):
        return OrderedDict([(value['dqpath'].split('/')[-1], sdc_value_reader(value))
                            for key, value in value.items()])
    elif isinstance(value, dict):
        if 'type' in value and 'value' in value:
            # value['type'] in some cases could also be a dict
            if (value['value'] is None or not isinstance(value['type'], str) or
                value['type'] not in type_to_function_map):
                return value['value']
            return type_to_function_map[value['type']](value['value'])
        else:
            return {key: sdc_value_reader(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [sdc_value_reader(item) for item in value]
    else:
        return value['value']


def pipeline_json_encoder(o):
    """Default method for JSON encoding of custom classes."""
    if hasattr(o, '_data'):
        return o._data
    raise TypeError('{} is not JSON serializable'.format(repr(o)))


def format_log(log_records):
    return '\n'.join([('{timestamp} [user:{user}] [pipeline:{entity}] '
                       '[runner:{runner}] [thread:{thread}] {severity} '
                       '{category} - {message} {exception}').format(timestamp=rec.get('timestamp'),
                                                                    user=rec.get('s-user'),
                                                                    entity=rec.get('s-entity'),
                                                                    runner=rec.get('s-runner'),
                                                                    thread=rec.get('thread'),
                                                                    severity=rec.get('severity'),
                                                                    category=rec.get('category'),
                                                                    message=rec.get('message'),
                                                                    exception=rec.get('exception'))
                      for rec in log_records])


# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_TIME_BETWEEN_CHECKS = 1  #:
DEFAULT_TIMEOUT = 60  #:
def wait_for_condition(condition, condition_args=None, condition_kwargs=None,
                       time_between_checks=DEFAULT_TIME_BETWEEN_CHECKS, timeout=DEFAULT_TIMEOUT,
                       time_to_success=0, success=None, failure=None):
  """Wait until a condition is satisfied (or timeout).

  Args:
      condition: Callable to evaluate.
      condition_args (optional): A list of args to pass to the
          ``condition``. Default: ``None``
      condition_kwargs (optional): A dictionary of kwargs to pass to the
          ``condition``. Default: ``None``
      time_between_checks (:obj:`int`, optional): Seconds between condition checks.
          Default: :py:const:`DEFAULT_TIME_BETWEEN_CHECKS`
      timeout (:obj:`int`, optional): Seconds to wait before timing out.
          Default: :py:const:`DEFAULT_TIMEOUT`
      time_to_success (:obj:`int`, optional): Seconds for the condition to hold true
          before it is considered satisfied. Default: ``0``
      success (optional): Callable to invoke when ``condition`` succeeds. A ``time``
          variable will be passed as an argument, so can be used. Default: ``None``
      failure (optional): Callable to invoke when timeout occurs. ``timeout`` will
          be passed as an argument. Default: ``None``

  Raises:
      :py:obj:`TimeoutError`
  """
  start_time = time()
  stop_time = start_time + timeout

  success_start_time = None

  while time() < stop_time:
      outcome = condition(*condition_args or [], **condition_kwargs or {})
      if outcome:
          success_start_time = success_start_time or time()
          if time() >= success_start_time + time_to_success:
              if success is not None:
                  success(time='{:.3f}'.format(time() - start_time))
              return
      else:
          success_start_time = None
      sleep(time_between_checks)

  failure(timeout=timeout)


class SeekableList(list):
    def get(self, **kwargs):
        try:
            return next(i for i in self if all(getattr(i, k) == v for k, v in kwargs.items()))
        except StopIteration:
            raise ValueError('Instance ({}) is not in list'.format(', '.join('{}={}'.format(k, v)
                                                                             for k, v in kwargs.items())))

    def get_all(self, **kwargs):
        return SeekableList(i for i in self if all(getattr(i, k) == v for k, v in kwargs.items()))


class MutableKwargs:
    """Util class with functions to update kwargs.

    Args:
        defaults (:obj:`dict`): default kwargs for the function.
        actuals (:obj:`dict`): actual kwargs passed to the function.
    """

    def __init__(self, defaults, actuals):
        self._defaults = defaults
        self._actuals = actuals

    def union(self):
        """Unions defaults with actuals.

        Returns:
            A py:obj:`dict` of unioned args.
        """
        unioned_kwargs = dict(self._defaults)
        unioned_kwargs.update(self._actuals)
        return unioned_kwargs

    def subtract(self):
        """Returns the difference between actuals and defaults based on keys.

        Returns:
            A py:obj:`dict` of subtracted kwargs.
        """
        return {key: self._actuals[key] for key in self._actuals.keys() - self._defaults.keys()}


def update_acl_permissions(api_client, resource_type, permission):
    """Util function mapping various api_client functions (update_acl_permissions) to the resource_type.

    Args:
        api_client (py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of API client.
        resource_type (:obj:`str`): Type of resource eg. 'JOB', 'PIPELINE'.
        permission (:py:class:`streamsets.sdk.sch_models.Permission`): A Permission object.
    """
    function_call_mapping = {'JOB': api_client.update_job_permissions,
                             'PIPELINE': api_client.update_pipeline_permissions,
                             'SDC': api_client.update_sdc_permissions,
                             'REPORT_DEFINITION': api_client.update_report_definition_permissions}
    return function_call_mapping[resource_type](permission, permission['resourceId'], permission['subjectId'])


def set_acl(api_client, resource_type, resource_id, acl_json):
    """Util function mapping various api_client functions (set_acl) to the resource_type.

    Args:
        api_client (py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of API client.
        resource_type (:obj:`str`): Type of resource eg. 'JOB', 'PIPELINE'.
        resource_id (:obj:`str`): Id of the resource (pipeline, job etc.).
        acl_json (:py:class:`streamsets.sdk.sch_models.Permission`): A Permission object.
    """
    function_call_mapping = {'JOB': api_client.set_job_acl,
                             'PIPELINE': api_client.set_pipeline_acl,
                             'SDC': api_client.set_sdc_acl,
                             'REPORT_DEFINITION': api_client.set_report_definition_acl}
    return function_call_mapping[resource_type](resource_id, acl_json)


def reversed_dict(forward_dict):
    """Reverse the key: value pairs to value: key pairs.

    Args:
        forward_dict (:obj:`dict`): Original key: value dictionary.

    Returns:
        An instance of (:obj:`dict`) with value: key mapping.
    """
    values = list(forward_dict.values())
    if len(set(values)) < len(values):
        logger.warning('The dictionary provided, is not one-one mapping. This could cause some consistency problems.')
    return dict(reversed(item) for item in forward_dict.items())


def get_open_output_lanes(stages):
    """Util function to get open output lanes from a set of stages.

    Args:
        stages (:py:obj:`streamsets.sdk.utils.SeekableList`) or
               (:obj:`list`): List of :py:class:`streamsets.sdk.sdc_models.Stage` instances.

    Returns:
        A (:obj:`set`) of open output (:obj:`str`) lanes.
    """
    output_lanes = set()
    input_lanes = set()
    for stage in stages:
        output_lanes.update({output_lane for output_lane in stage.output_lanes})
        input_lanes.update({input_lane for input_lane in stage._data['inputLanes']})
    return output_lanes - input_lanes


def determine_fragment_label(stages, number_of_open_output_lanes):
    """Util function to determine Pipeline Fragment Label.

    Args:
        stages (:py:obj:`streamsets.sdk.utils.SeekableList`) or
               (:obj:`list`): List of :py:class:`streamsets.sdk.sdc_models.Stage` instances.
        number_of_open_output_lanes (:obj:`int`): Number of open output lanes.

    Returns:
        An instance of :obj:`str`.
    """
    stage_types = {stage['uiInfo']['stageType'] for stage in stages}
    # Logic taken from: https://git.io/fjlL2
    label = 'Processors'
    if 'SOURCE' in stage_types:
        label = 'Origins'
    if number_of_open_output_lanes == 0:
        label = 'Destinations'
    return label
