"""
Parameters for geoviz
"""
from bokeh.palettes import *

def get_palette_colors(palette_label, ncolors):
    """ gets hexcodes of specified palette and reverses the order """
    color_palette = eval(f'{palette_label}{ncolors}').copy()
    color_palette.reverse()
    return color_palette

## shapefile height to width ratio
HEIGHT_RATIO = 0.6

## legal statistical area definition
LSAD = ['county', 'parish', 'city', 'borough', 'cty&bor', 'census area',
        'muny', 'municipio', 'municipality']

## all parameters
DEFAULTFORMAT = {'width':900, 'background_color':None,
                 'title':'', 'font':'futura', 'title_fontsize':'14pt',
                 'tools':'zoom_in,zoom_out,pan,reset,save', 'svg':None,
                 ## main map properties
                 'fill_alpha':1, 'line_color':'#d3d3d3', 'line_width':0.5, 'simplify':0,
                 'tooltip_text':'', 'hover_geolabel':'Area name', 'hover_ylabel':None,
                 ## color bar properties
                 'ncolors':5, 'palette':1, 'min':None, 'max':None,
                 'reverse_palette':False, 'lin_or_log':'lin',
                 'cbar_height':'auto', 'cbar_fontsize':None, 'cbar_textfmt':None,
                 'cbar_title':'', 'cbar_title_align':'center', 'cbar_style':None,
                 'cbar_tick_color':'black', 'cbar_tick_alpha':1, 'cbar_title_standoff_ratio':0.006,
                 ## state map properties
                 'state_outline_options':['none', 'before', 'after', 'both'], 'state_outline':'none',
                 'st_alpha':1, 'st_fill':None, 'st_line_color':'black', 'st_line_width':1}

## default palette options
palette_dict = {'sequential': ['RdPu', 'YlGnBu', 'YlOrRd'],
                'sequential_single' :['Blues', 'Greens', 'Purples'],
                'divergent': ['BrBG', 'RdBu', 'PiYG'],
                'categorical': ['Dark2_', 'Set1_', 'Set3_']}

##
max_n = {'sequential':9, 'sequential_single':9, 'divergent':11, 'categorical':8}

## get all palettes
PALETTES = {ptype:{} for ptype in palette_dict}
for ptype in palette_dict:
    for rank, label in enumerate(palette_dict[ptype]):
        PALETTES[ptype][label] = {}
        PALETTES[ptype][rank+1] = {}
        for n in range(3, max_n[ptype]+1):
            palette = get_palette_colors(label, n)
            PALETTES[ptype][label][n] = palette
            PALETTES[ptype][rank+1][n] = palette
## add custom locus color
for i in PALETTES['sequential'][2]:
    PALETTES['sequential'][2][i][-1] = '#0a3959'
