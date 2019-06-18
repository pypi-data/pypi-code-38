
import os, sys


# This project needs to import the skipole package, which should normally be immediately
# available if skipole has been installed on your system.

# from skipole import the WSGIApplication class which will be used to create a wsgi
# application, and exception classes which you will need in your functions

from skipole import WSGIApplication, FailPage, GoTo, ValidateError, ServerError, set_debug

# The set_debug function is used during development, it adds exception data to server error
# pages, and also stops javascript validation of input data on the client - this ensures that
# server validation can be tested

# You may also wish to import 'use_submit_list' whch can act as a decorator around your
# submit_data function. See the skipole documentation for details.

# the framework needs to know the location of the projectfiles directory holding this and
# other projects - specifically the skis and skiadmin projects
# The following line assumes, as default, that this script file is located beneath
# ...projectfiles/newproj/code/

PROJECTFILES = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
PROJECT = 'newproj'



##############################################################################
#
# Your code needs to provide your own version of the following three functions
#
# Minimal versions are provided below, you could either develop them here,
# or more usually, create further modules and packages and import them.
#
##############################################################################


def start_call(called_ident, skicall):
    "When a call is initially received this function is called."
    return called_ident


def submit_data(skicall):
    "This function is called when a Responder wishes to submit data for processing in some manner"
    return


def end_call(page_ident, page_type, skicall):
    """This function is called at the end of a call prior to filling the returned page with skicall.page_data,
       it can also return an optional session cookie string."""
    return


##############################################################################
#
# The above functions will be inserted into the skipole.WSGIApplication object
# and will be called as required
#
##############################################################################


# create the wsgi application
application = WSGIApplication(project=PROJECT,
                              projectfiles=PROJECTFILES,
                              proj_data={},
                              start_call=start_call,
                              submit_data=submit_data,
                              end_call=end_call,
                              url="/")

# This creates a WSGI application object. On being created the object uses the projectfiles location to find
# and load json files which define the project, and also uses the functions :
#     start_call, submit_data, end_call
# to populate returned pages.
# proj_data is an optional dictionary which you may use for your own purposes,
# it is included as the skicall.proj_data attribute


# The skis application must always be added, without skis you're going nowhere!
# The skis sub project serves javascript files required by the framework widgets.

skis_code = os.path.join(PROJECTFILES, 'skis', 'code')
if skis_code not in sys.path:
    sys.path.append(skis_code)
import skis
skis_application = skis.makeapp(PROJECTFILES)
application.add_project(skis_application, url='/lib')

# The add_project method of application, enables the added sub application
# to be served at a URL which should extend the URL of the main 'root' application.
# The above shows the main newproj application served at "/" and the skis library
# project served at "/lib"

# Note if you want to add further sub-projects you would typically:
#     Place the sub project code location on your sys.path
#     Import the sub project to obtain its wsgi application
#     Call application.add_project with the sub project application
#     and the url where it will be served.


# to deploy on a web server, you would typically install skipole on the web server,
# together with a 'projectfiles' directory containing the projects you want
# to serve (typically this project, and the skis project).
# you would then follow the web servers own documentation which should describe how
# to load a wsgi application.

# for example, using gunicorn3 by command line

# gunicorn3 -w 4 newproj:application

# Where gunicorn3 is the python3 version of gunicorn

#############################################################################
#
# You could remove everything below here when deploying and serving your
# finished application. The following lines are used to serve the project
# locally and add the skiadmin project for development.
#
#############################################################################

if __name__ == "__main__":


    ############################### THESE LINES ADD SKIADMIN FOR DEVELOPMENT ONLY #
    ###################### AND SHOULD BE REMOVED WHEN YOU DEPLOY YOUR APPLICATION #
                                                                                  #
    set_debug(True)                                                               #
    skiadmin_code = os.path.join(PROJECTFILES, 'skiadmin', 'code')                #
    if skiadmin_code not in sys.path:                                             #
        sys.path.append(skiadmin_code)                                            #
    import skiadmin                                                               #
    skiadmin_application = skiadmin.makeapp(PROJECTFILES, editedprojname=PROJECT) #
    application.add_project(skiadmin_application, url='/skiadmin')                #
                                                                                  #
    ###############################################################################

    # TYPICALLY WHEN YOUR FINISHED APPLICATION IS DEPLOYED, YOUR WEB SERVER WILL
    # IMPORT THIS MODULE AND THIS CODE WILL NEVER RUN AND COULD BE DELETED.
    # ALTERNATIVELY YOU MAY WISH TO ALTER THIS TO SERVE A DIFFERENT WEB SERVER
    # FROM THIS SCRIPT. FOR EXAMPLE, USING THE PYTHON 'WAITRESS' WEB SERVER:
    #
    # from waitress import serve
    # serve(application, host='0.0.0.0', port=8000)
    #

    from wsgiref.simple_server import make_server

    # serve the application
    host = "127.0.0.1"
    port = 8000

    httpd = make_server(host, port, application)
    print("Serving %s on port %s. Call http://localhost:%s/skiadmin to edit." % (PROJECT, port, port))
    httpd.serve_forever()

