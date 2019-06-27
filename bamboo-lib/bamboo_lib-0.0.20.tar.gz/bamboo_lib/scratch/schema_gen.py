from pums_core_schema import PUMS_MASTER_XML
from rw2 import gen_all
calc, to_hide = gen_all()
my_xml = PUMS_MASTER_XML.format(calculations=calc, to_hide=",".join(to_hide))
print(my_xml)
