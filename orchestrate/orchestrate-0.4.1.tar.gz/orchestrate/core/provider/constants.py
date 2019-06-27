from enum import Enum

from orchestrate.common import safe_format
from orchestrate.core.exceptions import OrchestrateException


class Provider(Enum):
  AWS = 1
  CUSTOM = 2


STRING_TO_PROVIDER = dict(
  aws=Provider.AWS,
  custom=Provider.CUSTOM,
)
PROVIDER_TO_STRING = dict((v, k) for (k, v) in STRING_TO_PROVIDER.items())


class UnknownProviderStringError(OrchestrateException):
  def __init__(self, provider_string):
    if provider_string is None:
      provider_error = "Please include a provider with your request."
    else:
      provider_error = safe_format("{} is not a supported provider.", provider_string.__repr__())

    super(UnknownProviderStringError, self).__init__(safe_format(
      "{} Supported providers are: {}",
      provider_error,
      ', '.join(STRING_TO_PROVIDER.keys()),
    ))
    self.provider_string = provider_string

def string_to_provider(provider_string):
  try:
    return STRING_TO_PROVIDER[provider_string.lower()]
  except (KeyError, AttributeError):
    raise UnknownProviderStringError(provider_string)


def provider_to_string(provider):
  try:
    return PROVIDER_TO_STRING[provider]
  except KeyError:
    raise NotImplementedError()
