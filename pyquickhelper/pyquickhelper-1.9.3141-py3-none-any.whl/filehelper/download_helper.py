"""
@file
@brief A function to download the content of a url.
"""
import socket
import gzip
import warnings
import urllib.error as urllib_error
import urllib.request as urllib_request
import http.client as http_client


class InternetException(Exception):

    """
    Exception for the function @see fn get_url_content_timeout
    """
    pass


def get_url_content_timeout(url, timeout=10, output=None, encoding="utf8", raise_exception=True, chunk=None, fLOG=None):
    """
    Downloads a file from internet (by default, it assumes
    it is text information, otherwise, encoding should be None).

    @param      url                 (str) url
    @param      timeout             (int) in seconds, after this time, the function drops an returns None, -1 for forever
    @param      output              (str) if None, the content is stored in that file
    @param      encoding            (str) utf8 by default, but if it is None, the returned information is binary
    @param      raise_exception     (bool) True to raise an exception, False to send a warnings
    @param      chunk               (int|None) save data every chunk (only if output is not None)
    @param      fLOG                logging function (only applies when chunk is not None)
    @return                         content of the url

    If the function automatically detects that the downloaded data is in gzip
    format, it will decompress it.

    The function raises the exception @see cl InternetException.
    """
    def save_content(content, append=False):
        "local function"
        app = "a" if append else "w"
        if encoding is not None:
            with open(output, app, encoding=encoding) as f:
                f.write(content)
        else:
            with open(output, app + "b") as f:
                f.write(content)

    try:
        if chunk is not None:
            if output is None:
                raise ValueError(
                    "output cannot be None if chunk is not None")
            app = [False]
            size = [0]

            def _local_loop(ur):
                while True:
                    res = ur.read(chunk)
                    size[0] += len(res)  # pylint: disable=E1137
                    if fLOG is not None:
                        fLOG("[get_url_content_timeout] downloaded",
                             size, "bytes")
                    if len(res) > 0:
                        if encoding is not None:
                            res = res.decode(encoding=encoding)
                        save_content(res, app)
                    else:
                        break
                    app[0] = True  # pylint: disable=E1137

            if timeout != -1:
                with urllib_request.urlopen(url, timeout=timeout) as ur:
                    _local_loop(ur)
            else:
                with urllib_request.urlopen(url) as ur:
                    _local_loop(ur)
            app = app[0]
            size = size[0]
        else:
            if timeout != -1:
                with urllib_request.urlopen(url, timeout=timeout) as ur:
                    res = ur.read()
            else:
                with urllib_request.urlopen(url) as ur:
                    res = ur.read()
    except (urllib_error.HTTPError, urllib_error.URLError) as e:
        if raise_exception:
            raise InternetException(
                "Unable to retrieve content, url='{0}'".format(url)) from e
        warnings.warn(
            "Unable to retrieve content from '{0}' exc: {1}".format(url, e), ResourceWarning)
        return None
    except socket.timeout as e:
        if raise_exception:
            raise InternetException(
                "Unable to retrieve content, url='{0}'".format(url)) from e
        warnings.warn("unable to retrieve content from {0} because of timeout {1}: {2}".format(
            url, timeout, e), ResourceWarning)
        return None
    except ConnectionResetError as e:
        if raise_exception:
            raise InternetException(
                "Unable to retrieve content, url='{0}'".format(url)) from e
        warnings.warn(
            "unable to retrieve content from {0} because of ConnectionResetError: {1}".format(url, e), ResourceWarning)
        return None
    except http_client.BadStatusLine as e:
        if raise_exception:
            raise InternetException(
                "Unable to retrieve content, url='{0}'".format(url)) from e
        warnings.warn(
            "Unable to retrieve content from '{0}' because of http.client.BadStatusLine: {1}".format(url, e), ResourceWarning)
        return None
    except http_client.IncompleteRead as e:
        if raise_exception:
            raise InternetException(
                "Unable to retrieve content url='{0}'".format(url)) from e
        warnings.warn(
            "Unable to retrieve content from '{0}' because of http.client.IncompleteRead: {1}".format(url, e), ResourceWarning)
        return None
    except ValueError as e:
        raise e
    except Exception as e:
        if raise_exception:
            raise InternetException(
                "Unable to retrieve content, url='{0}', exc={1}".format(url, e)) from e
        warnings.warn(
            "Unable to retrieve content from '{0}' because of unknown exception: {1}".format(url, e), ResourceWarning)
        raise e

    if chunk is None:
        if len(res) >= 2 and res[:2] == b"\x1f\x8B":
            # gzip format
            res = gzip.decompress(res)

        if encoding is not None:
            try:
                content = res.decode(encoding)
            except UnicodeDecodeError as e:
                # it tries different encoding

                laste = [e]
                othenc = ["iso-8859-1", "latin-1"]

                for encode in othenc:
                    try:
                        content = res.decode(encode)
                        break
                    except UnicodeDecodeError as e:
                        laste.append(e)
                        content = None

                if content is None:
                    mes = ["Unable to parse text from '{0}'.".format(url)]
                    mes.append("tried:" + str([encoding] + othenc))
                    mes.append("beginning:\n" + str([res])[:50])
                    for e in laste:
                        mes.append("Exception: " + str(e))
                    raise ValueError("\n".join(mes))
        else:
            content = res
    else:
        content = None

    if output is not None and chunk is None:
        save_content(content)

    return content
