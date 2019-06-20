"""
might be useful for oauth development

"""


import textwrap

class fake_host(object):
    """
    use as:

    with fake_host('syrus.hu'):
        server.serve(app)
    """

    hosts_files = {
        'posix': r'/etc/hosts',
        'nt': r'C:\Windows\System32\drivers\etc\hosts',
    }

    def __init__(self, host, ip='127.0.0.1'):
        self.insert = textwrap.dedent("""
        
        # Automagically inserted line for OAuth testing follows:
        {} {}

        """.format(ip, host))
        app.logger.debug(self.insert)

        # split between Windows and Linux (need sudo for that)
        try:
            self.hosts_file = hosts_files.get(os.name, None)
        except:
            raise ValueError('OS not supported')

    def __enter__(self):
        with open(hosts, 'r+') as h:
            # save the current in the tool and restore it on server stop
            x = h.read()
            print(x)
            if x.find(insert) == -1:
                h.truncate(0)
                h.seek(0)
                h.write(x + insert)
                print(insert)

    def __exit__(self, exc_type, exc_value, traceback):
        # restore hosts (this is not runninbg as a standalone script in production environment!)
        with open(hosts, 'r+') as h:
            # search for line with special comment and replace
            x = h.read()
            print(x)
            y = x.replace(insert, '')
            print(y)
            h.truncate(0)
            h.seek(0)
            h.write(y)
