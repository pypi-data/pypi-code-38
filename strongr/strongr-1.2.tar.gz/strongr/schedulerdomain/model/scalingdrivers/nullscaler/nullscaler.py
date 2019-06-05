from datetime import datetime, timedelta

from strongr.schedulerdomain.model.scalingdrivers.abstract import AbstractScaleOut, AbstractScaleIn, \
    AbstractVmTemplateRetriever


# The null-scaler ignores scalein and scaleout signals.

class NullScaler(AbstractScaleIn, AbstractScaleOut, AbstractVmTemplateRetriever):
    def __init__(self, config, *args, **kwargs):
        super(NullScaler, self).__init__(*args, **kwargs)
        # ignore config

    def get_vm_max_age(self, vm_name):
        return datetime.utcnow() + timedelta(days=100000)

    def get_templates(self):
        return ['localhost']

    def scalein(self, command):
        pass

    def scaleout(self, command):
        pass

