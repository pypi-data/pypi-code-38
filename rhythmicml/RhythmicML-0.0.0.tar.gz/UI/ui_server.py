from flask import Flask, render_template as renderTemplate, request;
from functools import wraps;
import json;
from . import helpers;

app = Flask(__name__);
host = "0.0.0.0";
port = "5000";

#==========================================================================
#====================      DECORATORS     =========================================
#==========================================================================
def checkPost(entry_point):

    @wraps(entry_point)
    def wrapper(*args, **kwargs):
        if request.method == "POST":

            return entry_point(*args, **kwargs);

        else:

            random_string_html = \
            """
            <div align = "center" style = "padding: 32px;">
            <h1>
            {}
            </h1>
            <a href = "/">main page</a>
            </div>
            """.format( helpers.randomString() );

            return random_string_html;

    return wrapper;


#==========================================================================

#==========================================================================
#====================      UI PAGES      ============================================
#==========================================================================
@app.route("/")
def index():
    """
    On the root page models catalogue is displayed and managed.
    """
    print(dir(helpers));
    print(helpers);
    models_list = helpers.getModelsList();
    
    return renderTemplate("index.html", title = "Catalogue", ui_caption = "Catalogue", models_list = models_list);

#==========================================================================

#==========================================================================

@app.route("/dashboard")
@app.route("/dashboard/<model_id>")
def dashboard(model_id = None):
    """
    /dashboard/<model_id>
    This is a particular model's dashboard, rendered with id.
    """

    return renderTemplate("dashboard.html", title = "Model Dashboard", ui_caption = "Model Dashboard", model_id = model_id);
#==========================================================================

#==========================================================================
#====================      HELPERS      ============================================
#==========================================================================

@app.route("/helpers/folders", methods = ["POST", "GET"])
@checkPost
def helperFolders():
    """
    /heplers/folders/
    receives local folder path in POST request;
    shows the folder contents, if accessible for the user.
    """

    the_folder = request.data.decode();

    folder_contents = helpers.scanFolder(the_folder);

    if folder_contents.__class__ == str: #the decorator returns an error message, if folderScan() execution fails
        return folder_contents;

    return renderTemplate("folder_contents.html", folder_contents = folder_contents, the_folder = the_folder);
#==========================================================================

#==========================================================================
@app.route("/helpers/folder_name_to_model_name", methods = ["POST", "GET"])
@checkPost
def helperFolderNameToModelName():
    """
    /helpers/foldername2modelname
    receives a path user picked path
    and returns a unique model name suggestion.
    """

    the_folder = request.data.decode();

    folder_base_name = helpers.getNameFromPath(the_folder);
    suggested_model_name = helpers.uniqueName(folder_base_name);

    return suggested_model_name;
#==========================================================================

#==========================================================================
@app.route("/helpers/add_new_model", methods = ["POST", "GET"])
@checkPost
def addModel():

    # model_name = request.data.model_name.decode();
    # the_folder = request.data.model_path.decode();

    data_json = request.data.decode();

    data = json.loads(data_json);

    new_model_name = data["model_name"];
    new_model_path = data["model_path"].replace(" ", "\\ ");

    execution_status = helpers.addNewModel(new_model_name, new_model_path);

    return execution_status;

#==========================================================================
#==========================================================================
#==========================================================================

def runUI(app, host = host, port = port):
    """
    run_ui(app, host = host, port = port):  
    app is a Flask app
    """

    app.run(debug = True, host = host, port = port);

if __name__ == "__main__":

    runUI(app);
