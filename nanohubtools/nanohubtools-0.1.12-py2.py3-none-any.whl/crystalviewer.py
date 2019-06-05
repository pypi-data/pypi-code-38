from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab
from hublib import ui
from .plotlywidget import FigureWidget
import math


class CrystalViewerTool (Rappturetool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_Structure', 
            'Nx',
            'Ny',
            'Nz',
            'Draw_miller_plane',
            'Draw_plane_1',
            'Draw_plane_2',
            'Draw_plane_3',
        ]
        parameters = self.parameters_structure
        kwargs.setdefault('title', 'CrystalViewer')
        Rappturetool.__init__(self, credentials, "crystal_viewer", parameters, extract_method="id", **kwargs)


        
    def displayOptions(self):
        html = '''
        <b>TODO</b>
        '''
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        
        children_structure.append(HTML(value=html))

        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

#        self.options['Nd'].visible = False
#        self.options['mun'].visible = False
#        self.options['mup'].visible = False
#        self.options['doping'].dd.observe(lambda b : setattr(self.options['Nd'], 'visible', (b['new'] != "intrinsic")), 'value')
#        self.options['mob'].dd.observe(lambda b : setattr(self.options['mun'], 'visible', (b['new'] == "yes")), 'value')
#        self.options['mob'].dd.observe(lambda b : setattr(self.options['mup'], 'visible', (b['new'] == "yes")), 'value')

        
        children_structure.append(self.options_but)
        container_structure.children = children_structure

        #container_introduction.children = children_introduction

        crystaltab = Tab()
        crystaltab.children = [container_structure]
        crystaltab.set_title(0, "Structure")
                
        self.options_cont.children = [crystaltab]
        
