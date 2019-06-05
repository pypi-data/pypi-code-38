from logging import getLogger
from os.path import join

from pyesgf.logon import ESGF_CREDENTIALS, ESGF_DIR, LogonManager
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory
from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler, ScrapyAgent
from twisted.internet.ssl import PrivateCertificate, optionsForClientTLS, platformTrust
from twisted.web.iweb import IPolicyForHTTPS
from zope.interface.declarations import implementer

from esgf_scraper import conf
from esgf_scraper.middlewares import ESGFRequest

logger = getLogger(__name__)


class CustomHTTP11DownloadHandler(HTTP11DownloadHandler):
    def __init__(self, settings):
        super(CustomHTTP11DownloadHandler, self).__init__(settings)
        self._auth_context_factory = ClientCertContextFactory(method=self._sslMethod)

    def download_request(self, request, spider):
        """Return a deferred for the HTTP download"""
        context_factory = (
            self._auth_context_factory
            if isinstance(request, ESGFRequest)
            else self._contextFactory
        )

        agent = ScrapyAgent(
            contextFactory=context_factory,
            pool=self._pool,
            maxsize=getattr(spider, "download_maxsize", self._default_maxsize),
            warnsize=getattr(spider, "download_warnsize", self._default_warnsize),
            fail_on_dataloss=self._fail_on_dataloss,
        )
        return agent.download_request(request)


@implementer(IPolicyForHTTPS)
class ClientCertContextFactory(ScrapyClientContextFactory):
    def creatorForNetloc(self, hostname, port):
        lm = LogonManager()
        if not lm.is_logged_on():
            if "openid" not in conf["auth"] or "password" not in conf["auth"]:
                logger.warning("No username or password available to authenticate")
            else:
                lm.logon_with_openid(conf["auth"]["openid"], conf["auth"]["password"])
        with open(join(ESGF_DIR, ESGF_CREDENTIALS)) as fh:
            raw_cert = fh.read()
        client_cert = PrivateCertificate.loadPEM(raw_cert)
        return optionsForClientTLS(
            hostname.decode("ascii"),
            trustRoot=platformTrust(),
            clientCertificate=client_cert,
            extraCertificateOptions={"method": self._ssl_method},
        )
