#
# Copyright (c) 2013-2019 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import aiohttp
import asyncio
import copy
import functools
import json as _json
import logging
import operator
import os
from pathlib import Path
from pkg_resources import parse_version
import ssl
import types
import yaml

from irma.shared.schemas import (
    apiid,
    ValidationError,
)
from irma.shared.schemas.v3 import (
    ArtifactSchema,
    FileExtSchema,
    FileKioskSchema,
    FileResultSchema,
    Paginated,
    ProbeSchema,
    ScanRetrievalCodeSchema,
    ScanSchema,
    TagSchema,
)


__all__ = ['AAPI', 'Config', 'IrmaError']

log = logging.getLogger("irma.irmacl")
logreq = logging.getLogger("irma.irmacl.requests")


def auth_guarded(call):
    @functools.wraps(call)
    async def wrapper(api, *args, **kwargs):
        try:
            await api._auth_free.wait()
            return await call(api, *args, **kwargs)
        except aiohttp.ClientResponseError as e:
            if e.status != 401 or not api.auth_enabled():
                raise

            log.info("Request denied, authentication required: %s", e)
            if api._auth_free.is_set():
                # Try to login only if there is not another pending task to do
                # it
                api._auth_free.clear()
                await api.login()
                api._auth_free.set()

            # Reopen file descriptors that were consumed by the previous
            # request
            data = kwargs.get('data')
            if data and isinstance(data, aiohttp.MultipartWriter):
                fds = (fd for fd, *_ in data._parts
                       if isinstance(fd, aiohttp.BufferedReaderPayload))
                for fd in fds:
                    # Reopen file descriptors
                    fd._value = open(fd._value.name, 'rb')

            # This call is unguarded. It will not try to login in case of
            # failure
            await api._auth_free.wait()
            return await call(api, *args, **kwargs)
            # NOTE: file descriptors are automatically closed by
            # aiohttp.MultipartWriter when consumed
    return wrapper


class IrmaError(Exception):
    pass


class Config:

    CONF_VENV = Path(os.environ.get("IRMA_CONF", ""))
    CONF_FILENAME = "irma.yml"
    CONF_FILES = [
        CONF_VENV / CONF_FILENAME if CONF_VENV.is_dir() else CONF_VENV,
        Path.cwd() / CONF_FILENAME,
        Path.home() / CONF_FILENAME,
        Path("/etc/irma") / CONF_FILENAME,
    ]

    @classmethod
    def autoload(cls):
        """ Load a configuration from a irma.yml file.

        :returns: the configuration from a well-located irma.conf file, or the
            default configuration if none is found

        """
        for conffile in cls.CONF_FILES:
            try:
                with conffile.open() as f:
                    log.info(
                        "Successfully read configuration from %r", conffile)
                    return Config(**yaml.safe_load(f))
            except OSError:
                log.info("Cannot read configuration from %r", conffile)
        log.warning(
            "No config file found, default configuration is applied")
        return Config()

    def __init__(
            self, api_endpoint="http://localhost/api/v3", timeout=300,
            verify=True, ca=None, cert=None, key=None,
            submitter="cli", submitter_id="", user="irma", password="irma"):
        """
        :param api_endpoint: url of the IRMA API (default
            "http://localhost/api/v3")
        :param timeout: time in seconds a request should be completed in before
            aborting it (default 300s). Not implemented
        :param verify: bool, verify server certificate (default True)
        :param ca: path to a CA file (default None)
        :param cert: path to the client certificate to use (default None)
        :param key: path to the client private key to use (default None)
        :param submitter: submitter to advertize to IRMA (default "cli")
        :param submitter_id: submitter specific identifier (default "")
        :param user, password: credentials to authenticate with (default
            "irma", "irma")

        """
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.verify = verify
        self.ca = ca
        self.cert = cert
        self.key = key
        self.submitter = submitter
        self.submitter_id = submitter_id
        self.user = user or submitter
        self.password = password

    @property
    def ssl(self):
        ctx = ssl.create_default_context()
        if self.verify:
            ctx.verify_mode = ssl.CERT_REQUIRED
            if self.cert and self.key:
                ctx.load_cert_chain(self.cert, self.key)
            if self.ca:
                ctx.load_verify_locations(self.ca)
        else:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx


class AAPI:

    IRMA_VERSION_MIN = parse_version("v3.0.0")
    IRMA_VERSION_MAX = parse_version("v4.0.0a0")

    def __init__(
            self, config=None, *, apicheck=True, limit=None,
            raw=False, loop=None):
        """
        :param config: Config object to use (default None ie.
            Config.autoload())
        :param apicheck: check that the IRMA counterpart is in the expected
            version (default True)
        :param limit: max number of simultaneous connections (default None).
            Not implemented
        :param raw: default value about response formating (default False)
        :param loop: event loop to use (default None ie.
            asyncio.get_event_loop())

        """
        config = config or Config.autoload()

        self.url = config.api_endpoint
        self.submitter = config.submitter
        self.submitter_id = config.submitter_id
        self.user = config.user
        self.password = config.password
        self.ssl = config.ssl

        self.apicheck = apicheck
        self.limit = limit
        self.raw = raw

        self._timeout = aiohttp.ClientTimeout(total=config.timeout)
        self._loop = loop or asyncio.get_event_loop()

        # Represent the absence of any authentication process. Needed to
        # authenticate only once when several 401 are received.
        self._auth_free = asyncio.Event(loop=self._loop)
        self._auth_free.set()

        self.session = None
        self.headers = {}

    async def __aenter__(self):
        self.session = await aiohttp.ClientSession(
            timeout=self._timeout, loop=self._loop).__aenter__()

        if self.apicheck:
            try:
                await self.check_version()
                log.info("Check API version: OK")
            except RuntimeWarning as e:
                log.warning(
                    "Check API version: IRMA version (%s) not included in"
                    " compatibility range [%s, %s[", e,
                    self.IRMA_VERSION_MIN, self.IRMA_VERSION_MAX)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.headers = {}
        return await self.session.__aexit__(exc_type, exc_value, traceback)

    async def _bare_get(
            self, route, session=None, query={}, stream=None, headers=None):
        """ Perform a GET request on a given route

        :param route: route to query
        :param session: custom session to use (default None)
        :param query: dict representing the fields to query
        :param stream: file descriptor to write the response into (default
            None). Especially useful when downloading a file.
        :param headers: additional headers for the requests (default None)
        :returns: body of the response
        :raises: aiohttp.ClientResponseError

        """
        if session is None:
            session = self.session

        url = self.url + route
        if headers is not None:
            h = self.headers.copy()
            h.update(headers)
        else:
            h = self.headers
        async with session.get(
                url, params=query, ssl=self.ssl, headers=h) as resp:
            log.info("GET %s", resp.url)
            logreq.debug(
                "%-3s -    GET - %s - %s - %s - %s",
                resp.status, self.url, route, _json.dumps(query), h
            )
            resp.raise_for_status()
            if stream:
                while True:
                    chunk = await resp.content.read(4096)
                    if not chunk:
                        break
                    stream.write(chunk)
            else:
                return await resp.read()

    _get = auth_guarded(_bare_get)

    async def _bare_post(
            self, route, session=None, headers=None, data=None, json=None):
        """ Perform a POST request on a given route

        :param route: route to query
        :param session: custom session to use (default None)
        :param headers: additional headers for the requests (default None)
        :param data, json: raw or json body to send in the request. Mutually
            exclusive. (default None)
        :returns: body of the response
        :raises: aiohttp.ClientResponseError

        """
        if session is None:
            session = self.session

        url = self.url + route
        if headers is not None:
            h = self.headers.copy()
            h.update(headers)
        else:
            h = self.headers
        log.info("POST %s", url)
        async with session.post(
                url, ssl=self.ssl, headers=h, data=data, json=json) as resp:
            body = (
                repr(data) if isinstance(data, aiohttp.MultipartWriter) else
                _json.dumps(data) if data else
                _json.dumps(json) if json else
                ''
            )

            logreq.debug(
                "%-3s -   POST - %s - %s - %s - %s",
                resp.status, self.url, route, body, h
            )
            resp.raise_for_status()
            return await resp.read()

    _post = auth_guarded(_bare_post)

    async def _bare_delete(
            self, route, session=None, headers=None, data=None, json=None):
        """ Perform a DELETE request on a given route

        :param route: route to query
        :param session: custom session to use (default None)
        :param headers: additional headers for the requests (default None)
        :param data, json: raw or json body to send in the request. Mutually
            exclusive. (default None)
        :returns: body of the response
        :raises: aiohttp.ClientResponseError

        """
        if session is None:
            session = self.session

        url = self.url + route
        if headers is not None:
            h = self.headers.copy()
            h.update(headers)
        else:
            h = self.headers
        log.info("DELETE %s", url)
        async with session.delete(
                url, ssl=self.ssl, headers=h, data=data, json=json) as resp:
            body = (
                repr(data) if isinstance(data, aiohttp.MultipartWriter) else
                _json.dumps(data) if data else
                _json.dumps(json) if json else
                ''
            )
            logreq.debug(
                "%-3s - DELETE - %s - %s - %s - %s",
                resp.status, self.url, route, body, h
            )
            resp.raise_for_status()
            return await resp.read()

    _delete = auth_guarded(_bare_delete)

    def _format(self, res, raw=None, schema=None):
        """ Format request result

        :param res: raw result of the request
        :param raw: bool, return unprocessed bytes (default None)
        :param schema: schema to process the response with (default None). If
        no schema is given the result is processed as native json
        :returns: formatted result of the request

        """
        raw = raw if raw is not None else self.raw
        if raw:
            return res
        elif schema is None:
            return _json.loads(res.decode())
        else:
            try:
                if isinstance(schema, (types.MethodType, types.FunctionType)):
                    # Dynamically load schema based on input data
                    res = _json.loads(res.decode())
                    schema = schema(res)()
                    return schema.load(res)
                else:
                    return schema.loads(res.decode())
            except ValidationError as e:
                log.error("deserialisation failed: %s", e)
                log.info("deserialisation failed - data: %s", e.data)

    def _askpage(self, offset=None, limit=None, query=None):
        """ Construct a query for asking a page of a paginated result

        :param offset: offset of the first element (default None)
        :param limit: size of the page (default None)
        :param query: pre-existing query the pagination have to be added to
            (default None). It is not modified by this method, but copied
        :returns: a query for pagination

        """
        query = copy.copy(query) if query is not None else {}

        if limit is not None:
            if limit < 1:
                raise ValueError("Page limit must be positive")
            query['limit'] = limit
        elif self.limit is not None:
            query['limit'] = self.limit

        if offset is not None:
            if offset < 0:
                raise ValueError("Page offset must be non-negative")
            query['offset'] = offset

        return query

    async def about(self, session=None, raw=None):
        """ Query information about IRMA itself

        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: dict with misc info

        """
        res = await self._get("/about", session)
        return self._format(res, raw)

    async def documentation(self, session=None, raw=None):
        """ Query the documentation of the API

        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: dict with the apispec documentation

        """
        res = await self._get("/about/documentation", session)
        return self._format(res, raw)

    async def check_version(self):
        """ Check that the queried IRMA API is compatible with this version of
            irmacl-async

        :raises: RuntimeWarning if incompatible versions

        """
        version = await self.about(raw=False)
        version = parse_version(version["version"])
        if not (self.IRMA_VERSION_MIN <= version < self.IRMA_VERSION_MAX):
            raise RuntimeWarning(version)

    async def login(self, username=None, password=None, session=None):
        """ Authenticate onto IRMA and set the headers accordingly

        :param username, password: credentials to use (default None)
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError

        """
        data = {
            "username": username or self.user,
            "password": password or self.password,
        }
        log.info("Authenticate as %s", data["username"])
        res = await self._bare_post("/auth/login", session, data=data)
        res = self._format(res, raw=False)
        self.headers["Authorization"] = "Bearer " + res["token"]

    def auth_enabled(self):
        return bool(self.password)

    @property
    def tags(self):
        """ Sub-API dedicated to tags
        """
        return TagsAAPI(self)

    @property
    def probes(self):
        """ Sub-API dedicated to probes
        """
        return ProbesAAPI(self)

    @property
    def files(self):
        """ Sub-API dedicated to files
        """
        return FilesAAPI(self)

    @property
    def scans(self):
        """ Sub-API dedicated to scans
        """
        return ScansAAPI(self)

    @property
    def artifacts(self):
        """ Sub-API dedicated to artifacts
        """
        return ArtifactsAAPI(self)

    @property
    def srcodes(self):
        """ Sub-API dedicated to srcodes
        """
        return SRCodeAAPI(self)

    @staticmethod
    async def fetchall(fetch, **kwargs):
        """ Fetch all items of a paginated result.

        :param fetch: function to call for the paginated result
        :param **kwargs: `fetch`'s arguments. Must not contain 'offset'.
        :returns: all items of the paginated route

        """
        if "offset" in kwargs:
            raise TypeError(
                "'offset' is an invalid keyword argument for fetchall()")

        # Fetch just the first page to get total and limit
        page = await fetch(offset=0, **kwargs)

        # NOTE: the following lines can be shrinked in a oneliner,
        # that's on purpose they are not ;)
        if page["limit"] is None:
            return page["items"]
        offsets = range(page["limit"], page["total"], page["limit"])
        queries = [fetch(offset=o, **kwargs) for o in offsets]
        pages = [page] + await asyncio.gather(*queries)
        return functools.reduce(operator.add, (p["items"] for p in pages))


class AAPIView:

    """ Specialized view on a generalist AAPI.
    """

    def __init__(self, api):
        self.api = api

    def __getattr__(self, name):
        return getattr(self.api, name)

    async def __aenter__(self):
        await self.api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.api.__aexit__(exc_type, exc_value, traceback)


class TagsAAPI(AAPIView):

    async def list(self, session=None, raw=None):
        """ List the entire collection of available tags

        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of tags

        """
        res = await self._get("/tags", session)
        schema = Paginated(TagSchema)()
        return self._format(res, raw, schema=schema)

    async def new(self, text, quiet=False, session=None, raw=None):
        """ Create a new tag

        :param text: name of the tag
        :param quiet: bool, do not raise an exception if the tag already
            exists (default False)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: a newly created tag
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError if the tag already exists

        """
        data = {"text": text}
        try:
            res = await self._post("/tags", session, data=data)
            return self._format(res, raw, schema=TagSchema())
        except aiohttp.ClientResponseError as e:
            if e.status != 400:
                raise
            log.warning(e)
            if not quiet:
                raise IrmaError("Tag '{}' already exists.".format(text))

    async def delete(self, tag, quiet=False, session=None):
        """ Delete a tag

        :param tag: tag or tag_id
        :param quiet: bool, do not raise an exception if the tag does not
            exist (default False)
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError if the tag does not exist

        """
        route = '/tags/{}'.format(apiid(tag))
        try:
            await self._delete(route, session)
        except aiohttp.ClientResponseError as e:
            if e.status != 404:
                raise
            log.warning(e)
            if not quiet:
                raise IrmaError("Tag {} does not exist.".format(tag))


class ProbesAAPI(AAPIView):

    async def list(self, offset=None, limit=None, session=None, raw=None):
        """ List the entire collection of available probes

        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of probes

        """
        query = self._askpage(offset, limit)

        res = await self._get("/probes", session, query)
        schema = Paginated(ProbeSchema)()
        return self._format(res, raw, schema=schema)


class FilesAAPI(AAPIView):

    def _prepare_file(self, content, filename):
        with aiohttp.MultipartWriter('form-data') as data:
            filesdata = aiohttp.payload.get_payload(content)
            filesdata.set_content_disposition(
                'form-data', name='files', filename=filename)
            data.append(filesdata)

            jsondata = {'submitter': self.submitter}
            if self.submitter_id:
                jsondata["submitter_id"] = self.submitter_id
            jsondata = aiohttp.JsonPayload(jsondata)
            jsondata.set_content_disposition('form-data', name='json')
            data.append(jsondata)
        return data

    async def list(self, offset=None, limit=None, session=None, raw=None):
        """ List a page of the collection of files

        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of files

        """
        return await self.search(None, None, None, offset, limit, session, raw)

    async def search(
            self, type=None, value=None, tags=None, offset=None, limit=None,
            session=None, raw=None):
        """ List a page of matching results of a query on files

        :param type: could be one of
            "name" search by filename (will look for partial match)
            "hash" search by hash value (no partial match)
            "virus_name" search by virus name
            "status" search by virus results (0: clean, 1: infected, -1: error)
        (default "name")
        :param value: the value to search for according to the specified type
        (default None)
        :param tags: one or a list of tags to filter out results (default None)
        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of files
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError if the search query is invalid

        """
        query = self._askpage(offset, limit)
        if type is not None:
            query["type"] = type
        if value is not None:
            query["value"] = value
        if tags is not None:
            query["tags"] = (
                ','.join(str(apiid(i)) for i in tags)
                if isinstance(tags, list)
                else str(apiid(tags))
            )

        try:
            res = await self._get("/files", session, query)
            schema = Paginated(FileExtSchema)()
            return self._format(res, raw, schema=schema)
        except aiohttp.ClientResponseError as e:
            if e.status in (400, 404,):
                log.warning(e)
                raise IrmaError("Invalid search query")
            raise

    async def results(
            self, file, offset=None, limit=None, session=None, raw=None):
        """ List a page of the results associated to file

        :param file: file or sha256
        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of results
        :raises: aiohttp.ClientResponseError

        """
        route = "/files/{}".format(apiid(file))
        query = self._askpage(offset, limit)
        res = await self._get(route, session, query)
        return self._format(res, raw, schema=FileResultSchema())

    async def add_tag(self, file, tag, quiet=False, session=None):
        """ Add a tag to a file

        :param file: file or sha256 to add the tag to
        :param tag: tag or id to add
        :param quiet: bool, do not raise an exception if the file is
            already tagged with this tag (default False)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError when tag is already present

        """
        route = "/files/{}/tags".format(apiid(file))
        try:
            await self._post(route, session, data={"tagid": apiid(tag)})
        except aiohttp.ClientResponseError as e:
            if e.status != 400:
                raise
            log.warning(e)
            if not quiet:
                raise IrmaError(
                    "File {} is already tagged with tag {}.".format(file, tag)
                )

    async def remove_tag(self, file, tag, quiet=False, session=None):
        """ Remove a tag from a file

        :param file: file or sha256 to remove the tag from
        :param tag: tag or id to remove
        :param quiet: bool, do not raise an exception if the file is not
            tagged with this tag (default False)
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError when tag cant be removed

        """
        route = "/files/{}/tags".format(apiid(file))
        try:
            await self._delete(route, session, data={"tagid": apiid(tag)})
        except aiohttp.ClientResponseError as e:
            if e.status != 400:
                raise
            log.warning(e)
            if not quiet:
                raise IrmaError(
                    "File {} is already NOT tagged with tag {}."
                    .format(file, tag)
                )

    async def upload(self, srcpath, session=None, raw=None):
        """ Create a new file from a local path

        :param srcpath: path to upload
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: newly created file_ext
        :raises: aiohttp.ClientResponseError

        """
        with srcpath.open('rb') as src:
            return await self.new(src, srcpath.as_posix(), session, raw)

    async def new(self, content, filename, session=None, raw=None):
        """ Create a new file

        :param content: bytes or file descriptor
        :param filename: name of the file for IRMA
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: newly created file_ext
        :raises: aiohttp.ClientResponseError

        """
        data = self._prepare_file(content, filename)
        res = await self._post("/files_ext", session, data=data)
        fe = self._format(res, raw, schema=FileExtSchema.dynschema)
        log.debug("  uploaded: %s/files_ext/%s", self.url, fe.id)
        return fe

    async def download(self, file, dstpath,
                       output_format="plain", session=None):
        """ Download a file from the API

        :param file: file or sha256 to download
        :param dstpath: path to write the downloaded file on
        :param output_format: download "plain" or "encrypted" file
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError

        """
        if output_format not in ("plain", "encrypted"):
            raise ValueError(
                "invalid output_format for download(): '{}'"
                .format(output_format)
            )
        headers = None
        if output_format == "encrypted":
            headers = {"Content-type": "application/vnd.irma.encrypted"}

        route = '/files/{}/content'.format(apiid(file))
        with dstpath.open('wb') as fd:
            await self._get(route, session, stream=fd, headers=headers)

    async def export(self, file, dstpath, session=None):
        """ Zip export of a file from the API

        :param file: file or sha256 to download
        :param dstpath: path to write the downloaded file on
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError

        """
        route = '/files/{}/content/export'.format(apiid(file))
        headers = {
            "Content-type": "application/zip"
            }
        with dstpath.open('wb') as fd:
            await self._get(route, session, stream=fd, headers=headers)

    async def delete(self, file, quiet=False, session=None):
        """ Delete a file on the API

        :param file: file or sha256 to unlink
        :param quiet: bool, do not raise an exception if the file has already
            been deleted (default False)
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError
        :raises IrmaError: if the file is already deleted

        """
        route = '/files/{}/content'.format(apiid(file))
        try:
            await self._delete(route, session)
        except aiohttp.ClientResponseError as e:
            if e.status != 400:
                raise
            log.warning(e)
            if not quiet:
                raise IrmaError("File {} doesn't exist.".format(file))

    async def delete_multi(self, type, value, session=None):
        """ Delete multiple files based on age or total size

        :param type: "age" or "size"
        :param value: max age or max total size of files to keep, all
            others will be deleted asynchronously
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError

        """
        query = {"type": type, "value": value}
        route = '/files/content'
        await self._delete(route, session, data=query)


class ScansAAPI(AAPIView):

    async def list(self, offset=None, limit=None, session=None, raw=None):
        """ List a page of the collection of scans

        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of scans
        :raises: aiohttp.ClientResponseError

        """
        query = self._askpage(offset, limit)
        res = await self._get('/scans', session, query)
        schema = Paginated(ScanSchema)()
        return self._format(res, raw, schema=schema)

    async def get(self, scan, session=None, raw=None):
        """ Query a scan

        :param scan: uuid or scan to query
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried scan
        :raises: aiohttp.ClientResponseError

        """
        route = "/scans/{}".format(apiid(scan))
        res = await self._get(route, session)
        return self._format(res, raw, schema=ScanSchema())

    async def waitfor(self, scan, session=None, raw=None):
        """ Wait for a scan to be finished and return it

        :param scan: uuid or scan to wait for
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried scan, once finished

        """
        while True:
            res = await self.get(scan, session, raw=False)
            if res.status < 50:
                await asyncio.sleep(1)
            else:
                break
        # Extra call to simplify 'raw' handling
        return await self.get(scan, session, raw)

    async def result(self, fileext, full=False, session=None, raw=None):
        """ Get detailed results on a specific scanned file

        :param fileext: fileext or uuid to get results of
        :param full: bool, get full results or shortened ones (default False)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the detailed results

        """
        route = "/files_ext/{}".format(apiid(fileext))
        query = {"formatted": "no"} if full else {}
        res = await self._get(route, session, query)
        return self._format(res, raw, schema=FileExtSchema.dynschema)

    async def results(
            self, scan, offset=None, limit=None, session=None, raw=None):
        """ Get results of a scan

        :param scan: uuid or scan to query
        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the detailed results

        """
        route = "/scans/{}/results".format(apiid(scan))
        query = self._askpage(offset, limit)
        res = await self._get(route, session, query)
        schema = Paginated(FileExtSchema, only=(
            'id', 'status', 'name', 'probes_finished', 'probes_total',
            'file.sha256', 'parent', 'submitter'))()
        return self._format(res, raw, schema=schema)

    async def download_report(
            self, scan, dstpath, output_format="csv", session=None):
        """ Download a scan's report from the API

        :param scan: scan or scan_id to export
        :param dstpath: path to write the downloaded file on
        :param output_format: the output_format required ("csv" or "txt")
            (default "csv")
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError, ValueError

        """
        if output_format not in ("csv", "txt"):
            raise ValueError(
                "invalid output_format for download_report(): '{}'"
                .format(output_format)
            )
        route = '/scans/{}/report'.format(apiid(scan))
        headers = {
            "Content-type":
                "text/plain" if output_format == "txt" else "text/csv",
        }

        with dstpath.open('wb') as fd:
            await self._get(route, session, stream=fd, headers=headers)

    async def extras(self, fileext, extras, session=None):
        """ Adjoin additional information to a file to scan

        :param fileext: fileext or fileext_id to add extras to
        :param extras: additional information ot add
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError

        """
        route = "/files_ext/{}/extras".format(apiid(fileext))
        await self._post(route, session, data=extras)

    async def launch(
            self, fileexts, session=None, raw=None, linger=False, *,
            probes=None, force=None, mimetype_filtering=None,
            resubmit_files=None):
        """ Create and launch a scan on already uploaded files

        :param fileexts: list of fileexts or uuids to enclose
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :param linger: bool, wait for the scan to complete (default False)
        :param probes: probes to run on (default None ie. all)
            only with superuser permission
        :param force, mimetype_filtering, resubmit_files: scan options (default
            None) only with superuser permission
        :returns: a newly created scan
        :raises: aiohttp.ClientResponseError

        """
        options = {}
        if force is not None:
            options['force'] = force
        if probes is not None:
            options['probes'] = probes
        if resubmit_files is not None:
            options['resubmit_files'] = resubmit_files
        if mimetype_filtering is not None:
            options['mimetype_filtering'] = mimetype_filtering

        data = {
            "files": [apiid(fe) for fe in fileexts]
        }
        if options:
            data["options"] = options
            res = await self._post("/scans/extended", session, json=data)
        else:
            res = await self._post("/scans", session, json=data)
        if linger:
            scan = self._format(res, raw=False, schema=ScanSchema())
            return await self.waitfor(scan, session, raw)
        else:
            return self._format(res, raw, schema=ScanSchema())

    async def scan(
            self, srcpaths, session=None, raw=None, linger=False, *,
            probes=None, force=None, mimetype_filtering=None,
            resubmit_files=None):
        """ Upload multiple files and run a scan on them

        :param srcpaths: a path or a collection of paths to scan
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :param linger: bool, wait for the scan to complete (default False)
        :param probes: probes to run on (default None ie. all)
            only with superuser permission
        :param force, mimetype_filtering, resubmit_files: scan options (default
            None) only with superuser permission
        :returns: a newly created scan
        :raises: aiohttp.ClientResponseError

        NOTE: if `srcpaths` is a single Path, then the `/scan/quick` API route
        will be used and so `probes`, `force`, `mimetype_filtering` and
        `resubmit_files` are ignored. Send a collection of one file to prevent
        it.

        """
        if isinstance(srcpaths, Path):
            srcpath = srcpaths  # just to be clear
            with srcpath.open('rb') as src:
                data = self.api.files._prepare_file(src, srcpath.as_posix())
                res = await self._post("/scans/quick", session, data=data)
            if linger:
                scan = self._format(res, raw=False, schema=ScanSchema())
                return await self.waitfor(scan, session, raw)
            else:
                return self._format(res, raw, schema=ScanSchema())
        else:
            files = [self.api.files.upload(p) for p in srcpaths]
            files = await asyncio.gather(*files)
            return await self.launch(
                files, session, raw, linger, probes=probes, force=force,
                mimetype_filtering=mimetype_filtering,
                resubmit_files=resubmit_files)

    async def cancel(self, scan, session=None, raw=None):
        """ Cancel a running scan

        :param scan: uuid or scan to cancel
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the canceled scan
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError if the scan is already finished

        """
        route = "/scans/{}/cancel".format(apiid(scan))
        try:
            res = await self._post(route, session)
            return self._format(res, raw, schema=ScanSchema())
        except aiohttp.ClientResponseError as e:
            if e.status != 400:
                raise
            raise IrmaError(
                "Scan {} finished, cannot cancel it".format(apiid(scan))
            )


class ArtifactsAAPI(AAPIView):

    async def list(self, offset=None, limit=None, session=None, raw=None):
        """ List a page of the collection of artifacts

        :param offset: offset for pagination (default None)
        :param limit: custom limit for pagination (default None)
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried page of the list of artifacts
        :raises: aiohttp.ClientResponseError

        """
        query = self._askpage(offset, limit)
        res = await self._get('/artifacts', session, query)
        schema = Paginated(ArtifactSchema)()
        return self._format(res, raw, schema=schema)

    async def get(self, artifact, session=None, raw=None):
        """ Query an artifact

        :param artifact: uuid or artifact to query
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: the queried artifact
        :raises: aiohttp.ClientResponseError

        """
        route = "/artifacts/{}".format(apiid(artifact))
        res = await self._get(route, session)
        return self._format(res, raw, schema=ArtifactSchema())

    async def download(self, artifact, dstpath, session=None):
        """ Download an artifact from the API

        :param artifact: artifact or uuid to download
        :param dstpath: path to write the downloaded artifact on
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError

        """
        route = '/artifacts/{}/content'.format(apiid(artifact))
        with dstpath.open('wb') as fd:
            await self._get(route, session, stream=fd)

    async def delete(self, artifact, quiet=False, session=None):
        """ Delete an artifact on the API

        :param artifact: artifact or uuid to unlink
        :param quiet: bool, do not raise an exception if the artifact has
            already been deleted (default False)
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError
        :raises IrmaError: if the artifact is already deleted

        """
        route = '/artifacts/{}/content'.format(apiid(artifact))
        try:
            await self._delete(route, session)
        except aiohttp.ClientResponseError as e:
            if e.status != 400:
                raise
            log.warning(e)
            if not quiet:
                raise IrmaError("Artifact {} doesn't exist.".format(artifact))


class SRCodeAAPI(AAPIView):

    async def new(self, scan, session=None, raw=None):
        """ Create a new scan retrieval code

        :param scan: scan or scan id
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: a newly created srcode

        """
        route = "/scan_retrieval_codes"
        res = await self._post(route, session, data={"scan_id": apiid(scan)})
        return self._format(res, raw, schema=ScanRetrievalCodeSchema())

    async def get(self, srcode, session=None, raw=None):
        """ Get a scan by srcode

        :param srcode: scan retrieval code value
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: an srcode object

        """
        route = "/scan_retrieval_codes/{}".format(apiid(srcode))
        res = await self._get(route, session)
        return self._format(res, raw, schema=ScanRetrievalCodeSchema())

    async def get_directories(self, srcode, session=None, raw=None):
        """ Get the list of directory of files from the scan. It can be used to
        recreate a directory Tree.

        :param srcode: scan retrieval code value
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: list of directories

        """
        route = "/scan_retrieval_codes/{}/directories".format(apiid(srcode))
        res = await self._get(route, session)
        return self._format(res, raw)

    async def get_results(self, srcode, path='/', session=None, raw=None):
        """ Get the results (list of files supporting pagination) from a scan
        identify by a SRCode. Specify the `path` in which you want to have the
        results.

        :param srcode: scan retrieval code value
        :param path: directory from which you want the results
        :param session: custom session to use (default None)
        :param raw: bool, return unprocessed bytes (default None)
        :returns: list of files information

        """
        route = "/scan_retrieval_codes/{}/results".format(apiid(srcode))
        res = await self._get(route, session, {"path": path})
        return self._format(res, raw, schema=Paginated(FileKioskSchema)())

    async def download_file(self, srcode, file, dstpath, session=None):
        """ Download a file from the Scan Retrieval Code API.

        :param srcode: scan retrieval code value
        :param file: file id to download
        :param dstpath: path to write the downloaded file on
        :param session: custom session to use (default None)
        :raises: aiohttp.ClientResponseError
        :raises: IrmaError on wrong srcode, scan not finished or file
        potentially harmful

        """
        try:
            route = '/scan_retrieval_codes/{}/results/{}/content' \
                .format(apiid(srcode), apiid(file))
            with dstpath.open('wb') as fd:
                await self._get(route, session, stream=fd)
        except aiohttp.ClientResponseError as e:
            if e.status != 403:
                raise
            log.warning(e)
            raise IrmaError("Download forbidden")
