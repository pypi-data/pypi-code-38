'''
svgutils_pq_example.py
======================

:Author: |author_name|
:Release: |version|
:Date: |today|


Purpose
=======

|description|

Make a figure layout using svgutils


Usage and options
=================

These are based on docopt_, see examples_.

.. _docopt: https://github.com/docopt/docopt

.. _examples: https://github.com/docopt/docopt/blob/master/examples/options_example.py


Usage:
       svgutils_pq_example.py  (--plotA=<name>) (--plotB=<name>) [-O FILE]
       svgutils_pq_example.py  [-h | --help]

Options:
    --plotA=<name> Panel A plot as svg
    --plotB=<name> Panel B plot as svg
    -O FILE        Output file name
    -h --help      Show this screen


Documentation
=============

    For more information see:

        |url|

    Also see examples and information from svgutils:

    - https://neuroscience.telenczuk.pl/?p=331
    - http://svgutils.readthedocs.io/en/latest/tutorials/composing_multipanel_figures.html
    - https://svgutils.readthedocs.io/en/latest/compose.html
    - http://cairosvg.org/
    - https://inkscape.org/en/

'''
##############
# Get all the modules needed
# System:
import os
import sys
import glob

# Options and help:
import docopt

# Get svgutils and PDF converter if not using Inkscape:
from svgutils.compose import *
import cairosvg

# Import this project's module, uncomment if building something more elaborate:
#try:
#    import module_template.py

#except ImportError:
#    print("Could not import this project's module, exiting")
#    raise
##############

##############
def plotSVG(plotA, plotB, outfile = 'F1_test'):
    ''' Plots a two panel figure with plots provided using svgutils.
    '''
    # Only svg can be output with svgutils:
    #figure_number = '1'
    #figure_name = 'test'
    outfile = outfile
    file_format_in = 'svg'
    file_format_out = 'pdf'
    layout_name_1 = str('{}.{}'.format(outfile,
                                       file_format_in))
    layout_name_2 = str('{}.{}'.format(outfile,
                                       file_format_out))
    paper_size_w = "20cm" # A4 paper is 210 mm x 197 mm
    paper_size_h = "12cm"
    my_layout = Figure(paper_size_w, paper_size_h, # read as width, height
                              # Panel() groups all elements belonging to one plot/panel
                              Panel(
                                  SVG(plotA).scale(0.70), # scale only the plot, not the text
                                  # Place Text() after SVG(), otherwise it doesn't plot:
                                  Text("A", 0, 20, size = 11, weight = 'bold'),
                                  ).move(20, 20), # hor, vert move
                              Panel(
                                  SVG(plotB).scale(0.70),
                                  Text("B", 0, 20, size = 11, weight = 'bold'),
                                  ).move(380, 20), # placed here move() is applied to all
                                                   # elements of the panel
                                                   # move(280, 0) will move the figure 280
                                                   # px horizontally
                              #Grid(20, 20) # Generates a grid of horizontal and vertical lines 
                                           # labelled with their position in pixel units
                                           # Use to test if figure is placed correctly, then
                                           # comment out. Use within Figure()
                                           # e.g. Figure(XXX, Grid(20, 20), Panel(XXX))
                                )

    # Save the Figure:
    my_layout.save(layout_name_1)
    print('''Saved multi-panel plot of
             {}
             and
             {}
             as file: {}'''.format(plotA, plotB, layout_name_1))

    # Convert SVG file to PDF:
    #cairosvg.svg2pdf(url = layout_name_1,
    #                 write_to = layout_name_2
    #                 )
    # Alternatively with inkscape:                                         
    os.system('''inkscape --without-gui \
                          --export-area-drawing \
                          --export-margin=1 \
                          --file={} \
                          --export-pdf={}'''.format(layout_name_1,
                                                    layout_name_2)
                 )
    #--export-dpi=300 \
    print('Saved file as pdf: {}'.format(layout_name_2))
##############

##############
def main():
    ''' with docopt main() expects a dictionary with arguments from docopt()
    docopt will automatically check your docstrings for usage, set -h, etc.
    '''
    options = docopt.docopt(__doc__)
    welcome_msg = str('\n' + 'Welcome to svgutils_pq_example.py ')
    print(welcome_msg)
    docopt_error_msg = str('\n' + 'svgutils_pq_example.py  exited due to an error.' + '\n')
    docopt_error_msg = str(docopt_error_msg
                           + '\n'
                           + 'Try svgutils_pq_example.py --help'
                           + '\n' + '\n'
                           + 'Options in place:'
                           + '\n'
                           + str(options)
                           + '\n'
                           )

    try:
        # Names of the plots to read in, these have to be svg files:
        if options['--plotA'] and options['--plotB']:
            plotA= str(options['--plotA']).strip('[]').strip("''")
            plotB= str(options['--plotB']).strip('[]').strip("''")
            # Call function above to plot with files provided:
            if options['-O']:
                outfile = str(options["-O"]).strip('[]').strip("''")
                plotSVG(plotA, plotB, outfile = outfile)
            elif not options['-O']:
                plotSVG(plotA, plotB)

        elif not options['--plotA'] and not options['--plotB']:
            plotA = 'pandas_DF_gender_glucose_boxplot.svg'
            plotB = 'pandas_DF_age_histogram.svg'
            print(''' Using default plots
                      {}
                      {}'''.format(plotA, plotB))
            # Call function above with default file names:
            plotSVG(plotA, plotB)

        else:
            print('No plots in svg format provided. Exiting...')
            print(docopt_error_msg)
            sys.exit()

    # Handle exceptions:
    except docopt.DocoptExit:
        print(docopt_error_msg)
        raise
############

############ 
# Finish and exit with docopt arguments:
if __name__ == '__main__':
    sys.exit(main())
############
