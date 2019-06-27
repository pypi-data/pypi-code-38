import json
import warnings

import sigopt

from orchestrate.common import safe_format


def read_suggestion(config):
  if config.is_enabled:
    with open(config.suggestion_location) as suggestion_fp:
      raw_suggestion = json.load(suggestion_fp)
  else:
    raw_suggestion = {'assignments': {}}
  return sigopt.objects.Suggestion(raw_suggestion)

def assignment_getter(config, logger, suggestion):

  def assignment(name, default=None):
    if config.is_enabled:
      try:
        return suggestion.assignments[name]
      except KeyError:
        warnings.warn(safe_format(
          "There is no assignment for the parameter `{}`, returning the default value: {}",
          name,
          default,
        ), RuntimeWarning)
        logger.write_log('unknown_parameter', {
          'name': name,
          'default': default,
        })
        return default
    else:
      return suggestion.assignments.get(name, default)

  return assignment
