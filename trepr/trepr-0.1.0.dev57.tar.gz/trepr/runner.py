import trepr.io
import trepr.dataset
import trepr.processing
import aspecd.utils
import trepr.fitpy_interface

imp1 = trepr.io.SpeksimImporter(
    '/home/popp/nas/DatenBA/PCDTBT-ODCB/X-Band/080K/messung17/')
data_set1 = trepr.dataset.ExperimentalDataset()
data_set1.import_from(imp1)
imp2 = trepr.io.SpeksimImporter(
    '/home/popp/nas/Python/Daten/NDITBT-Sa542/messung01/')
data_set2 = trepr.dataset.ExperimentalDataset()
data_set2.import_from(imp2)
imp3 = trepr.io.SpeksimImporter(
    '/home/popp/nas/Python/Daten/NDITBT-Sa544/messung01/')
data_set3 = trepr.dataset.ExperimentalDataset()
data_set3.import_from(imp3)
pretrigger = trepr.processing.PretriggerOffsetCompensation()
data_set1.process(pretrigger)
data_set2.process(pretrigger)
data_set3.process(pretrigger)
averaging = trepr.processing.Averaging(0, [4.e-7, 6.e-7], 'axis')
data_set1.process(averaging)
data_set2.process(averaging)
data_set3.process(averaging)
data_sets = data_set2
yaml = aspecd.utils.Yaml()
yaml.read_from('fitpy-input.yaml')
parameter_dict = yaml.dict

obj = trepr.fitpy_interface.FitPyInterface()
obj.datasets = data_sets
obj.parameters = parameter_dict
obj.fit()
