from pybpodapi.settings import TARGET_BPOD_FIRMWARE_VERSION

if TARGET_BPOD_FIRMWARE_VERSION == '20':
	from pybpodapi.bpod.hardware.output_channels.bpod0_7_9_fw20 import OutputChannel
elif TARGET_BPOD_FIRMWARE_VERSION == '17':
	from pybpodapi.bpod.hardware.output_channels.bpod0_7_9_fw13 import OutputChannel
elif TARGET_BPOD_FIRMWARE_VERSION == '15':
	from pybpodapi.bpod.hardware.output_channels.bpod0_7_9_fw13 import OutputChannel
elif TARGET_BPOD_FIRMWARE_VERSION == '13':
	from pybpodapi.bpod.hardware.output_channels.bpod0_7_9_fw13 import OutputChannel
elif TARGET_BPOD_FIRMWARE_VERSION == '9':
	from pybpodapi.bpod.hardware.output_channels.bpod0_7_5_fw9 import OutputChannel
else:
	from pybpodapi.bpod.hardware.output_channels.bpod0_7_5_fw9 import OutputChannel
