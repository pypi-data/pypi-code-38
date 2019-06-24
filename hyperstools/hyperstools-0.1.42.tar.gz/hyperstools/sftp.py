# encoding: utf-8
import logging
from traceback import format_exc

import paramiko
from .lib import retry

logger = logging.getLogger("tools")


@retry(log=logger)
def _getSFTP(username="", password="", host="", port=""):
    sftp = None
    try:
        t = paramiko.Transport((host, port))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        logger.info("Connected SFTP.")
    except Exception:
        logger.error(f"连接失败:{format_exc()}")
    return sftp


class SFTP(object):

    """封装paramiko库，连接sftp"""

    def __init__(
        self, username=None, password=None, host=None, port=None, **kwargs
    ) -> None:
        """初始化

        :identify: dict: TODO

        """
        self._client = _getSFTP(username, password, host, port)

    def downloadLocal(self, serverPath, path):
        try:
            self._client.get(serverPath, path)
        except Exception:
            logger.error(f"下载文件失败:{format_exc()}")

    def download(self, serverPath, obj):
        try:
            self._client.getfo(serverPath, obj)
        except Exception:
            logger.error(f"下载文件失败:{format_exc()}")

    def upload(self, obj, serverPath):
        """上传文件到sftp

        :obj: StringIO 或BytesIO
        :serverPath: sftp地址
        :returns: sftp的返回值

        """
        obj.seek(0)
        try:
            return self._client.putfo(obj, serverPath)
        except Exception:
            logger.error(f"上传文件失败:{format_exc()}")

    def mkdir(self, path):
        try:
            return self._client.mkdir(path)
        except Exception:
            logger.error(f"创建目录失败:{format_exc()}")

    def listdir(self, path):
        try:
            return self._client.listdir(path)
        except Exception:
            logger.error(f"获取文件列表失败:{format_exc()}")
            return []

    def stat(self, path):
        try:
            return self._client.stat(path)
        except Exception:
            logger.error(f"获取文件信息失败:{format_exc()}")

    def close(self):
        return self._client.close()

    def __enter__(self):
        return self

    def __exit(self, *args):
        self._client.close()
