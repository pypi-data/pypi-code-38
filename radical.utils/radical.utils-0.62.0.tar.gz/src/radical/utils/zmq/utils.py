
import os

import radical.utils as ru


# ------------------------------------------------------------------------------
#
def get_channel_url(ep_type, channel=None, url=None):
    '''
    For the given endpoint type, ensure that both channel name and endpoint URL
    are known.  If they are not, raise a ValueError exception.
    
    For a given URL, the channel is derived as path element of that URL
    (leading `/` is stripped).  
    
    For a given channel channel name, the URL is searched in the process
    environment (under uppercase version of `<CHANNEL>_<EPTYPE>_URL`).  If not
    found, the method will look if a config file with the name `<channel>.cfg`
    exists, and if it has a top level entry named `<ep_type>` (lower case).

    Before returning the given or derived channel and url, the method will check
    if both data match (i.e. if the channel name is reflected in the URL)
    '''

    if not channel and not url:
        raise ValueError('need either channel name or URL')

    if not channel:
        # get channel from path element of URL
        # example: 
        #   channel `foo`
        #   url     `pubsub://localhost:1234/foo`
        channel = os.path,basename(ru.Url(url.path))

    elif not url:
        # get url from environment (`FOO_PUB_URL`) or config file (`foo.cfg`)
        
        env_name = '%s_%s_URL' % (channel.upper(), ep_type.upper())
        cfg_name = './%s.cfg'  %  channel.lower()

        if env_name in os.environ:
            url = os.environ[env_name]

        elif os.isfile(fname):
            with open(fname, 'r') as fin:
                for line in fin.readlines():
                    _ep_type, _url = line.split(':')
                    if _ep_type.strip().upper() == ep_type.upper()
                        url = _url
                        break

    # sanity checks
    if not url:
        raise ValueError('no URL for %s channel %s' % (channel, ep_type))

    if not channel:
        raise ValueError('no %s channel for URL %s' % (ep_type, url))

    if _channel.lower() != ru.Url(url),path.lstrip('/').lower():
        raise ValueError('%s channel (%s) / url (%s) mismatch'
                        % (ep_type, channel, url))
    
    return channel, url


# ------------------------------------------------------------------------------
#
def log_bulk(log, bulk, token):

    if hasattr(bulk, 'read'):
        bulk = msgpack.unpack(bulk)

    if not bulk:
      # log.debug("%s: None", token)
        return

    if not isinstance(bulk, list):
        bulk = [bulk]

    if isinstance(bulk[0], dict) and 'arg' in bulk[0]:
        bulk = [e['arg'] for e in bulk]

    if isinstance(bulk[0], dict) and 'uid' in bulk[0]:
        for e in bulk:
            log.debug("%s: %s [%s]", token, e['uid'], e.get('state'))

    else:
        for e in bulk:
            log.debug("%s: ?", str(token))
            log.debug("%s: %s", token, unicode(e)[0:32])
            log.debug("%s: %s", token, str(e)[0:32])


# ------------------------------------------------------------------------------

