import os

from hapiclient import hapi
from hapiplotserver.plot import plot
from hapiplotserver.viviz import prepviviz, req2slug

def app(conf):

    from flask import Flask, request, redirect, send_from_directory, make_response, url_for
    application = Flask(__name__)

    loglevel = conf['loglevel']
    cachedir = conf['cachedir']
    server_usecache = conf['usecache']
    appdir = os.path.abspath(os.path.dirname(__file__))

    @application.route("/favicon.ico")
    def favicon():
        if request.args.get('server') is None:
            return send_from_directory(appdir + "/html/", "favicon.ico")

    @application.route("/")
    def main():
        if request.args.get('server') is None:
            return send_from_directory(appdir + "/html/", "index.html")

        format = request.args.get('format')
        if format is None:
            format = 'png'

        if format == 'png':
            ct = {'Content-Type': 'image/png'}
        elif format == 'pdf':
            ct = {'Content-Type': 'application/pdf'}
        elif format == 'svg':
            ct = {'Content-Type': 'image/svg+xml'}
        else:
            ct = {'Content-Type': 'text/html'}

        server = request.args.get('server')
        if server is None:
            return 'A server argument is required, e.g., /?server=...', 400, {'Content-Type': 'text/html'}

        dataset = request.args.get('id')
        if dataset is None and format != 'gallery':
            return 'A dataset id argument is required, e.g., /?server=...&id=...', 400, {'Content-Type': 'text/html'}

        parameters = request.args.get('parameters')
        if parameters is None and format != 'gallery':
            return 'A parameters argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

        start = request.args.get('time.min')
        if start is None and format != 'gallery':
            return 'A time.min argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

        stop = request.args.get('time.max')
        if start is None and format != 'gallery':
            return 'A time.max argument is required if format != "gallery", e.g., /?server=...&id=...&parameters=...', 400, {'Content-Type': 'text/html'}

        meta = None
        if start is None and format != 'gallery':
            try:
                meta = hapi(server, dataset)
                start = meta['startDate']
            except Exception as e:
                return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}

        if stop is None and format != 'gallery':
            if meta is None:
                try:
                    meta = hapi(server, dataset)
                except Exception as e:
                    return 'Could not get metadata from ' + server, 400, {'Content-Type': 'text/html'}
            stop = meta['stopDate']

        usecache = request.args.get('usecache')
        if usecache is None:
            usecache = True
        elif usecache.lower() == "true":
            usecache = True
        elif usecache.lower() == "false":
            usecache = False
        else:
            return 'usecache must be true or false', 400, {'Content-Type': 'text/html'}

        if server_usecache is False and usecache is True:
            usecache = False
            if loglevel == 'debug':
                print('app(): Application configuration has usecache=False so request to use cache is ignored.')

        transparent = request.args.get('transparent')
        if transparent is None:
            transparent = True
        elif transparent.lower() == "true":
            transparent = True
        elif transparent.lower() == "false":
            transparent = False
        else:
            return 'transparent must be true or false', 400, {'Content-Type': 'text/html'}

        dpi = request.args.get('dpi')
        if dpi is None:
            dpi = 300
        else:
            dpi = int(dpi)
            if dpi > 1200 or dpi < 1:
                return 'dpi must be <= 1200 and > 1', 400, {'Content-Type': 'text/html'}

        figsize = request.args.get('figsize')
        if figsize is None:
            figsize = (7, 3)
        else:
            figsizearr = figsize.split(',')
            figsize = (float(figsizearr[0]), float(figsizearr[1]))
            # TODO: Set limits on figsize?

        if format == 'gallery':
            indexhtm, vivizhash = prepviviz(server, dataset, parameters, start, stop, **conf)
            # Get full URL
            url = url_for("viviz", _external=True)
            red = url + indexhtm + "#" + vivizhash
            print("hapiplotserver.app.main(): Redirecting to " + red)
            return redirect(red, code=302)

        # Plot options
        opts = {'cachedir': cachedir, 'usecache': usecache, 'loglevel': loglevel, 'format': format, 'figsize': figsize, 'dpi': dpi, 'transparent': transparent}

        img = plot(server, dataset, parameters, start, stop,  **opts)

        ct['Content-Length'] = len(img[0])

        if img[1] is not None:
            ct["X-Error"] = img[1]

        return img[0], 200, ct

    # Serve index.htm for /viviz/ request
    @application.route("/viviz/")
    def viviz():
        pass

    # Serve static files
    @application.route("/viviz/"+"<path:filename>")
    def vivizf(filename):
        fname, fext = os.path.splitext(cachedir+"/viviz/" + filename)
        response = make_response(send_from_directory(cachedir+"/viviz", filename))
        if not fext:
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = 'inline'
        return response

    @application.errorhandler(500)
    def internal_error(error):
        print(error)

    return application
