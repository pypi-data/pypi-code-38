# flake8: noqa
import base64
import traceback

import koji
# Import krbV from here so we don't have to redo the whole try except that Koji does
from koji import krbV, PythonImportError, AuthError, AUTHTYPE_KERB


class ClientSession(koji.ClientSession):
    """The koji.ClientSession class with patches from upstream."""

    # This backport comes from https://pagure.io/koji/pull-request/1187
    def krb_login(self, principal=None, keytab=None, ccache=None, proxyuser=None, ctx=None):
        """Log in using Kerberos.  If principal is not None and keytab is
        not None, then get credentials for the given principal from the given keytab.
        If both are None, authenticate using existing local credentials (as obtained
        from kinit).  ccache is the absolute path to use for the credential cache. If
        not specified, the default ccache will be used.  If proxyuser is specified,
        log in the given user instead of the user associated with the Kerberos
        principal.  The principal must be in the "ProxyPrincipals" list on
        the server side.  ctx is the Kerberos context to use, and should be unique
        per thread.  If ctx is not specified, the default context is used."""

        try:
            # Silently try GSSAPI first
            if self.gssapi_login(principal, keytab, ccache, proxyuser=proxyuser):
                return True
        except Exception as e:
            if krbV:
                e_str = ''.join(traceback.format_exception_only(type(e), e))
                self.logger.debug('gssapi auth failed: %s', e_str)
                pass
            else:
                raise

        if not krbV:
            raise PythonImportError(
                "Please install python-krbV to use kerberos."
            )

        if not ctx:
            ctx = krbV.default_context()

        if ccache != None:
            ccache = krbV.CCache(name=ccache, context=ctx)
        else:
            ccache = ctx.default_ccache()

        if principal != None:
            if keytab != None:
                cprinc = krbV.Principal(name=principal, context=ctx)
                keytab = krbV.Keytab(name=keytab, context=ctx)
                ccache.init(cprinc)
                ccache.init_creds_keytab(principal=cprinc, keytab=keytab)
            else:
                raise AuthError('cannot specify a principal without a keytab')
        else:
            # We're trying to log ourself in.  Connect using existing credentials.
            cprinc = ccache.principal()

        self.logger.debug('Authenticating as: %s', cprinc.name)
        sprinc = krbV.Principal(name=self._serverPrincipal(cprinc), context=ctx)

        ac = krbV.AuthContext(context=ctx)
        ac.flags = krbV.KRB5_AUTH_CONTEXT_DO_SEQUENCE | krbV.KRB5_AUTH_CONTEXT_DO_TIME
        ac.rcache = ctx.default_rcache()

        # create and encode the authentication request
        (ac, req) = ctx.mk_req(server=sprinc, client=cprinc,
                               auth_context=ac, ccache=ccache,
                               options=krbV.AP_OPTS_MUTUAL_REQUIRED)
        req_enc = base64.encodestring(req)

        # ask the server to authenticate us
        (rep_enc, sinfo_enc, addrinfo) = self.callMethod('krbLogin', req_enc, proxyuser)
        # Set the addrinfo we received from the server
        # (necessary before calling rd_priv())
        # addrinfo is in (serveraddr, serverport, clientaddr, clientport)
        # format, so swap the pairs because clientaddr is now the local addr
        ac.addrs = tuple((addrinfo[2], addrinfo[3], addrinfo[0], addrinfo[1]))

        # decode and read the reply from the server
        rep = base64.decodestring(rep_enc)
        ctx.rd_rep(rep, auth_context=ac)

        # decode and decrypt the login info
        sinfo_priv = base64.decodestring(sinfo_enc)
        sinfo_str = ac.rd_priv(sinfo_priv)
        sinfo = dict(zip(['session-id', 'session-key'], sinfo_str.split()))

        if not sinfo:
            self.logger.warn('No session info received')
            return False
        self.setSession(sinfo)

        self.authtype = AUTHTYPE_KERB
        return True
