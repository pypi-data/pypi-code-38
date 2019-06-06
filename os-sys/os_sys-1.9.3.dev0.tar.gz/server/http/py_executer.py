def exec_return(code, re):
    import sys
    from io import StringIO
    import contextlib
    class Proxy(object):
        def __init__(self,stdout,stringio):
            self._stdout = stdout
            self._stringio = stringio
        def __getattr__(self,name):
            if name in ('_stdout','_stringio','write'):
                object.__getattribute__(self,name)
            else:
                return getattr(self._stringio,name)
        def write(self,data):
             self._stdout.write(data)
             self._stringio.write(data)

    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = Proxy(sys.stdout,stdout)
        yield sys.stdout
        sys.stdout = old


    with stdoutIO() as s:
        request = re
        exec(code)
    return s.getvalue()

def run_py(response):
    if '<?py' in response and 'py?>' in response:
        request = ''
        code = response.split('<?py')[1:]
        for p in code:
            to_do = p.split('py?>')[0]
            try:
                a = exec_return(to_do, request)
            except Exception as ex:
                a = 'python internal server error Traceback: %s' % ex
                codet = 500
            response = response.replace('<?py'+to_do+'py?>', a, 1)
    return response
