class PlatformNotSupported(Exception):
  pass


class SmartCardError(Exception):
  pass


class SmartCardFindKeyObjectError(SmartCardError):
  def __init__(self, key_id):
    key_id = key_id[0] if isinstance(key_id, tuple) else key_id
    super().__init__('Could not get key for key id: {}.'.format(key_id))


class SmartCardWrongPinError(SmartCardError):
  pass


class SmartCardNotPresentError(SmartCardError):
  pass


class SmartCardSigningError(SmartCardError):
  def __init__(self, data):
    super().__init__('Unable to create signature for data:\n{}\n'.format(data))
