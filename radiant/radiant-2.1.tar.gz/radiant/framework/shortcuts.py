from django.shortcuts import render


#----------------------------------------------------------------------
def brython_render(request, template, debug=0, context={}):
    """"""

    context['brython_template'] = template
    context['debug'] = debug
    #context['splash_name'] = splash_name

    return render(request, "radiant/brythonframework/base.html", context)


