import time
import json
from urllib import parse as urlParse
from urllib import request as urlRequest
from urllib import error as urlError
from . import AError


class Jenkins_Error(AError.Error):
    pass


class Jenkins_URLError(Jenkins_Error):
    pass


class Jenkins_TimeoutError(Jenkins_Error):
    pass


def isBuilding(jenkinsURL, jobName):
    jobInfo = json.loads(urlRequest.urlopen('%s/job/%s/api/json' % (jenkinsURL, jobName)).read().decode('UTF-8'))
    if jobInfo['queueItem'] is not None:
        return True
    lastBuildInfo = json.loads(urlRequest.urlopen(jobInfo['lastBuild']['url'] + '/api/json').read().decode('UTF-8'))
    return lastBuildInfo['building']


def requestBuild(jenkinsURL, jobName, token, params=None, timeout=60):
    """
    开始一次远程构建.
    该函数将阻塞直到构建真正开始（一开始构建条目会被排队）
    :param params a sequence of tuple(key, value)
    :param timeout 如果阻塞超过该时间，则抛出Jenkins_TimeoutError
    :return 构建条目ID
    """
    finalParams = [('token', token)]
    if params is not None:
        finalParams.extend(params)

    buildAction = 'build' if params is None else 'buildWithParameters'
    try:
        response = urlRequest.urlopen('%s/job/%s/%s' % (jenkinsURL, jobName, buildAction), urlParse.urlencode(finalParams).encode('UTF-8'))
    except urlError.URLError as e:
        raise Jenkins_URLError(str(e))

    # 等待直到排队条目开始构建
    startWaitTime = time.time()
    while True:
        queuedItemInfo = json.loads(urlRequest.urlopen(response.getheader('Location') + 'api/json').read().decode('UTF-8'))
        if 'executable' in queuedItemInfo and queuedItemInfo['executable'] is not None:
            return queuedItemInfo['executable']['number']

        time.sleep(1)
        if time.time() - startWaitTime > timeout:
            raise Jenkins_TimeoutError('Timeout')
