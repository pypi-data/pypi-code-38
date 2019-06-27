from flask import request, abort, url_for


class IPCheck(object):
    def __init__(self, app, ip_list, logging_enabled=False):
        """
        Initialize IPBlock and set up a before_request handler in the
        app.

        You can pass in IP list to verify if incoming request coming from
        a trusted server or not.

        Set Logging_enabled to true to see the IP of the incoming request in the log file
        :param app:
        :param ip_list:
        :param logging_enabled:
        """
        self.logger = None
        self.IP_LIST = ip_list
        if logging_enabled:
            self.logger = app.logger

        app.before_request(self.check_whitelisting)

    def check_whitelisting(self):
        """
        checks the IP if it belongs to the input range, otherwise it throws HTTPErr:403 error
        :return:
        """

        # To avoid unnecessary database queries, ignore the IP check for
        # requests for static files
        if request.path.startswith(url_for('static', filename='')):
            return

        # Some static files might be served from the root path (e.g.
        # favicon.ico, robots.txt, etc.). Ignore the IP check for most
        # common extensions of those files.
        ignored_extensions = ('ico', 'png', 'txt', 'xml')
        if request.path.rsplit('.', 1)[-1] in ignored_extensions:
            return

        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

        if ip:
            if self.logger:
                self.logger.info("Incoming request from IP: {}".format(ip))
            if ip not in self.IP_LIST:
                abort(403)
        else:
            return "No IP found, Please check Nginx config", 412
