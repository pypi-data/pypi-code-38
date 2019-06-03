import webbrowser
from pkg_resources import resource_listdir
from pkg_resources import resource_filename

def browse():
    """
    list all of the vignettes available for this package
    """
    outs = _get_vignette_titles()
    
    if len(outs) > 0:
        stri = "\nAvailable documents: \n"
        print(stri)
        for i in outs:
            print(i)
        print("\nTo open use e.g load_vignette('" + str(outs[0]) + "')\n")
    else:
        print("No documents available")
        
def load_vignette(name):
    """
    grab a particular vignette from the package
    """
    outs = _get_vignette_titles()
    if any(n == name for n in outs):
        path = resource_filename("jrpyml",'vignettes/')
        webbrowser.open_new(path + name)
    else:
        print("Does not match any vignettes")
        browse()
    
def _get_vignette_titles():
    x = resource_listdir("jrpyml",'vignettes/')
    # grab only those which are pdfs or html
    pdfs = [s for s in x if ".pdf" in s]
    htmls = [s for s in x if ".html" in s]
    outs = pdfs + htmls
    return outs

