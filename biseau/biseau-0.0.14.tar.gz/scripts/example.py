# encoding: utf8
"""Biseau script explaining the interface.

Comment/delete/modify `DISABLED = True`
in order to get it available from Biseau.

An easy way to test it is to add in GUI this rule:

    link(1,1).
    color(1,blue):- ichbineinberliner.
    color(1,green):- examplescriptwashere.

The node 1 will tell you if yes or no the scripts ran,
depending of the checkbox you checks.


"""

NAME = "Example script"
DISABLED = True  # comment/delete/modify this to enable this script in Biseau




# define the I/O of the scripts, if necessary based on the options.
#  note that the inputs/outputs function get the options, because they could
#  define the I/O. INPUTS/OUTPUTS attributes are not callable, just a set
#  defining the maximal I/O.
#  Here the input is constant whatever the options, but outputs depends.
def outputs(ich_bin_ein_berliner):
    return {'examplescriptwashere/0'} | ({'ichbineinberliner/0'} if ich_bin_ein_berliner else set())
INPUTS = {}
OUTPUTS = outputs(True)


def run_on(context:str, *,
           # Now begins the options of the script, shown in GUI with a widget.
           # Supported types: bool (checkbox), int/float (spinbox), str (text)
           # The default value gives the initial state of the widget in GUI.

           # here is a boolean
           ich_bin_ein_berliner:bool=True):


    # We do what we want with the context.
    context += '\nexamplescriptwashere.'

    # Which will probably depend of the options.
    if ich_bin_ein_berliner:
        context += '\nichbineinberliner.'

    # But the important part is to return it.
    return context
