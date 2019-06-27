import os
def setup(_setup):
    from setuptools import setup as _setup_
    def setup_(data):
        return _setup_(os.path.join(_data, '\nreturn=True,\nsetup=False,'))
    return setup_(_setup)
if __name__ == '__main__':
    print('wrong setup script')
    raise SystemExit()
