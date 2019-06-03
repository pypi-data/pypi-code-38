import os,sys, numpy as np
thisdir = os.path.abspath(os.path.dirname(__file__))
if thisdir not in sys.path:
    sys.path.insert(0, thisdir)

template = """<?xml version="1.0"?>

<!DOCTYPE SampleAssembly[
   {shape_file_entries}	
]> 
<SampleAssembly name="ClampCell"
   max_multiplescattering_loops_among_scatterers="1"
   max_multiplescattering_loops_interactM_path1="1"
   min_neutron_probability="0.01"
 >
    {sample_blocks} 

    <LocalGeometer registry-coordinate-system="InstrumentScientist"> 
        {geom_regs} 
    </LocalGeometer>

    <Environment temperature="300*K"/>

</SampleAssembly>
"""
def shape_file_entry(shape_name, shape_fileName):
  return """ <!ENTITY {shape_name} SYSTEM "{shape_fileName}.xml">
""".format(shape_name=shape_name, shape_fileName=shape_fileName)


def sample_block(name, shape_name, formula, strutureFiletype):
  return """  <PowderSample name="{name}" type="sample">
    <Shape>
      &{shape_name};
    </Shape>
    <Phase type="crystal">
      <ChemicalFormula>{formula}</ChemicalFormula>
      <{strutureFiletype}file>{formula}.{strutureFiletype}</{strutureFiletype}file>
    </Phase>
  </PowderSample>
""".format(name=name, shape_name=shape_name, formula=formula, strutureFiletype=strutureFiletype)

scatterers = {
     ('outer-body', 'shapeAl', 'outer-body-geom', 'Al', 'xyz'),   # (name, shape_name, formua)
     ('inner-sleeve', 'shapeCu', 'inner-sleeve-geom',  'Cu', 'xyz'),
     ('sample', 'shapeSample', 'sample_geom', 'Si', 'xyz'),
     ('collimator', 'shapeColl','coll_geometry', 'B4C', 'cif'),
}

def makeSAXML(sampleassembly_fileName, scatterers=scatterers):

   shape_file_entries = [shape_file_entry(shape_name, shape_fileName) for name, shape_name, shape_fileName, formula,strutureFiletype  in scatterers]
   shape_file_entries='\n'.join(shape_file_entries)
   sample_blocks = [sample_block(name, shape_name, formula,strutureFiletype) for name, shape_name, shape_fileName, formula,strutureFiletype  in scatterers]
   sample_blocks = '\n'.join(sample_blocks)
   lines = ['<Register name="{}" position="(0,0,0)" orientation="(0,0,0)"/>' .format(name) for name, shape_name, shape_fileName, formula,strutureFiletype in scatterers]
   geom_regs = '\n '.join(lines)
   text = template.format(shape_file_entries=shape_file_entries, sample_blocks=sample_blocks, geom_regs=geom_regs)
   with open(os.path.join(thisdir, '../sample/sampleassembly_{}.xml'.format(sampleassembly_fileName)), "w") as sam_new:
       sam_new.write(text)
   # return(sampleassembly_fileName)
   return()






