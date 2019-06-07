import dataclasses


@dataclasses.dataclass()
class SystemInformation:
    hostname: str
    os_version: str
    serial_number: str

    cpu_utilization: float

    memory_total: int
    memory_free: int


@dataclasses.dataclass()
class DeviceInformation:
    device_name: str
    vendor_name: str


@dataclasses.dataclass()
class Interface:
    port_id: str
    type: str
    intrusion_alert: str
    enabled: str
    status: str
    mode: str
    mdi_mode: str
    flow_control: str
