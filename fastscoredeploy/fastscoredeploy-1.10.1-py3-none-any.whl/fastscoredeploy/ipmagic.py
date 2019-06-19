from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import types
import json
import six
from .Model import Model
from fastscore import Schema, Stream

import __main__ as main_mod

@magics_class
class IPMagic(Magics):

    @cell_magic
    def model(self, line, cell):
        """
        Magic used to indicate that the contents of the cell
        define a FastScore model. Creates a Model object that
        can be interacted with from within the notebook. If the model's
        schemas are already defined in the notebook, they'll automatically
        be added to the model.

        Format is:
        %%model [model name] [model type (optional)]
        ... [model code]
        """
        linetxt = [x for x in str(line).split(' ') if len(x) > 0]
        mname = linetxt[0]
        celltxt = str(cell)

        mtype = 'python'
        if six.PY3:
            mtype = 'python3'
        if len(linetxt) > 1:
            mtype = linetxt[1]
        mymodel = Model(name=mname, mtype=mtype, source=celltxt)
        for slot in mymodel.options.schema:
            sch_name = mymodel.options.schema[slot]
            if sch_name in main_mod.__dict__:
                schema = main_mod.__dict__[sch_name]
                mymodel.schemas[sch_name] = schema

        main_mod.__dict__[mname] = mymodel
        print(('Model loaded and bound to {} variable.'.format(mname)))
        return

    @cell_magic
    def schema(self, line, cell):
        """
        Magic used to indicate that the contents of the cell define a
        FastScore schema. Creates a Schema object that can be interacted
        with from within the notebook.

        Format is
        %%schema [schema name]
        {
            "name":"an example schema"
            "type":"record",
            "fields":[...]
        }
        """
        linetxt = str(line)
        celltxt = str(cell)
        myschema = Schema(name=linetxt, source=json.loads(celltxt))
        main_mod.__dict__[linetxt] = myschema
        print(('Schema loaded and bound to {} variable'.format(linetxt)))
        return

    @cell_magic
    def stream(self, line, cell):
        """
        Magic used to indicate that the contents of a cell define a
        FastScore stream. Creates a Stream object that can be
        interacted with from within the notebook.

        Format is
        %%stream [stream name]
        ...
        """
        linetxt = str(line)
        celltxt = str(cell)
        mystream = Stream(name=linetxt, desc=json.loads(celltxt))
        main_mod.__dict__[linetxt] = mystream
        print(('Stream loaded and bound to {} variable'.format(linetxt)))
        return



# The following lines make it so that running "import ipmagic"
# adds the magic above to the notebook

# In order to actually use these magics, you must register them with a
# running IPython.  This code must be placed in a file that is loaded once
# IPython is up and running:
ip = get_ipython()
# You can register the class itself without instantiating it.  IPython will
# call the default constructor on it.
ip.register_magics(IPMagic)
