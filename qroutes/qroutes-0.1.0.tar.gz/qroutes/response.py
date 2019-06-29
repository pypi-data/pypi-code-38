import os

def swagger_startup_response(path):
    '''Response handler that returns a swagger startup script

    absolute path to swagger resource

    '''
    def swagger_startup_inner(request):
        scheme = request['scheme']
        host = request['headers']['Host']

        return {
                'status': 200,
                'headers': [('Content-Type', 'application/javascript')],
                'body': '''
                    window.onload = function() {
                        // Begin Swagger UI call region
                        const ui = SwaggerUIBundle({
                            url: "%s://%s%s",
                            dom_id: "#swagger-ui",
                            deepLinking: true,
                            presets: [
                                SwaggerUIBundle.presets.apis,
                                SwaggerUIStandalonePreset
                            ],
                            plugins: [
                                SwaggerUIBundle.plugins.DownloadUrl
                            ],
                            layout: "StandaloneLayout"
                       })
                       // End Swagger UI call region

                        window.ui = ui
                    }
                ''' % (scheme, host, path) 
        }
    return swagger_startup_inner