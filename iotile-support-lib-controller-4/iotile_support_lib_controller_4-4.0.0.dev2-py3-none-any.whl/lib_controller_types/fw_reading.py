from iotile.core.hw.reports.report import IOTileReading

def convert(arg):
    if isinstance(arg, IOTileReading):
        return arg

    raise ValueError("fw_reading can only be created from an IOTileReading instance")

#Formatting Functions
def default_formatter(arg, **kwargs):
    return str(arg)
