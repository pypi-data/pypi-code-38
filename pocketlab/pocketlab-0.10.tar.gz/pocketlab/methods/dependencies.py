__author__ = 'rcj1492'
__created__ = '2017.06'
__license__ = 'MIT'

from pocketlab import __module__

def import_boto3(resource_name=''):

    if not resource_name:
        resource_name = __module__

    try:
        import boto3
    except:
        raise ImportError('Use of %s requires the boto3 module.\nTry: pip3 install boto3' % resource_name)

def import_paramiko(resource_name=''):

    if not resource_name:
        resource_name = __module__

    help_text = """
(windows)       download Visual Studio C++ Express
                pip3 install pycrypto
                                
PLEASE NOTE:    pycrypto import process is corrupted and requires a correction
                https://github.com/dlitz/pycrypto/issues/110
                ..\site-packages\Crypto\Random\OSRNG\nt.py"""

    from platform import uname
    local_os = uname()
    if local_os.system in ('Windows'):
        try:
            import paramiko
            import scp
        except:
            raise ImportError('Use of %s on Windows requires paramiko module.\nTry: pip3 install paramiko\n%s' % (resource_name, help_text))

def import_scp(resource_name=''):

    if not resource_name:
        resource_name = __module__

    help_text = """
PLEASE NOTE:    SCP protocol requires SCP installed on Remote Host

(aws-linux)     sudo yum install -y git"""

    print(help_text)

if __name__ == '__main__':
    import_scp()
