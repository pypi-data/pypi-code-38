from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise


class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # SR can set custom periodicity
    self.setPeriodicity(float(self.getConfig('frequency', 2)))

  def sense(self):
    """
      Check state of the filename

      state can be empty or not-empty
    """

    filename = self.getConfig('filename')
    state = self.getConfig('state')
    url = self.getConfig('url').strip()

    try:
      result = open(filename).read()
    except Exception as e:
      self.logger.error(
        "ERROR %r during opening and reading file %r" % (e, filename))
      return

    if state == 'empty' and result != '':
      message_list = ['ERROR %r not empty' % (filename,)]
      if url:
        message_list.append(', content available at %s' % (url,))
      self.logger.error(''.join(message_list))
    elif state == 'not-empty' and result == '':
      self.logger.error(
          "ERROR %r empty" % (filename,))
    else:
      self.logger.info("OK %r state %r" % (filename, state))

  def anomaly(self):
    return self._anomaly(result_count=3, failure_amount=3)
