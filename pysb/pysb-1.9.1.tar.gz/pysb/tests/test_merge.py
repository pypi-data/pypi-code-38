# from pysb.examples.earm_1_3 import model as earm
from pysb.examples.bax_pore import model as bax_pore
from pysb.importers.bngl import model_from_bngl
from pysb.tests.test_importers import _bngl_location
from pysb.merge import NoOverlapMerge
from pysb.export.pysb_flat import PysbFlatExporter

def test_merge_basic():
    # egfr = model_from_bngl(_bngl_location('egfr_net'))
    # print(egfr.monomers)
    # print(earm.monomers)
    # print(bax_pore.monomers)
    m_merge = NoOverlapMerge(bax_pore, bax_pore).merge()
    print(PysbFlatExporter(m_merge).export())
    raise

