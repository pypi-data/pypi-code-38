from tqdm import tqdm, tqdm_notebook
import ipywidgets as widgets
from IPython.display import Javascript, display

# create_code_cell
import base64
from IPython.utils.py3compat import str_to_bytes, bytes_to_str

def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def progressbar(itr):
    if isnotebook():
        return tqdm_notebook(itr)
    else:
        return tqdm(itr)


def typingdropdown(o, n):
    '''
    from demyst.shiny import typingdropdown

    user_df = pd.DataFrame(columns=['first', 'last'])
    blackfin_df = user_df.copy()

    typingdropdown(user_df, blackfin_df)
    '''
    if isnotebook():

        def on_change(v):
            old_column_name = v.owner.description
            new_column_name = v.new
            n.rename(index=str, columns={old_column_name: new_column_name}, inplace=True)

        # TODO: retrieve types from Blackfin
        types = ['passthrough', 'domain', 'first_name', 'last_name', 'street_address', 'city']

        for input in list(o):
            w = widgets.Dropdown(
                    options=types,
                    value='passthrough',
                    description=input,
                    disabled=False,
                )
            w.observe(on_change, names='value')
            display(w)

    else:
        print('Not supported in non Ipython interface')

def create_code_cell(code='', where='below'):
    """Create a code cell in the IPython Notebook.

    Parameters
    code: unicode
        Code to fill the new code cell with.
    where: unicode
        Where to add the new code cell.
        Possible values include:
            at_bottom
            above
            below"""
    encoded_code = bytes_to_str(base64.b64encode(str_to_bytes(code)))
    display(Javascript("""
        var code = IPython.notebook.insert_cell_{0}('code');
        code.set_text(atob("{1}"));
    """.format(where, encoded_code)))

def generatehandler():

    s = """input = results[0]

def handler(input):
    \"\"\"Write your data function here\"\"\"
    return(input)

handler(input)"""

    create_code_cell(s)

def generatehandlerbutton():
    if isnotebook():

        def on_button_clicked(b):
            generatehandler()

        l = widgets.Layout(width='100%', height='60px')
        w = widgets.Button(
            description='Create Data Function',
            disabled=False,
            button_style='info', # for white test
            tooltip='Click me',
            icon='',
            layout=l
        )
        w.style.button_color = '#3dbded'
        w.style.font_weight = '700'

        w.on_click(on_button_clicked)
        display(w)
