from .network import Host


class HostConfig(object):

    def __init__(self):
        self.entries = []

    def add(self, source_path: str, target_path: str):
        self.entries += [(source_path, target_path)]

    def render(self) -> str:
        return "CONF=\"" + ",".join(
            ["{};{};{{netboot_ip}};300".format(entry[0], entry[1]) for entry in
             self.entries]) + "\"" if self.entries else None


class ConfigFile(object):

    def __init__(self, host: Host, host_config: HostConfig, netboot_ip: str):
        self.host = host
        self.host_config = host_config
        self.netboot_ip = netboot_ip

    def write(self):
        with open('config.{}'.format(self.host.ipv4_address_hex), 'w') as kiwi_config_file:
            kiwi_config_file.write(
                "IMAGE=/dev/ram1;{};1.42.3;{};10096\n".format(self.host.image_type, self.netboot_ip))
            kiwi_config_file.write("UNIONFS_CONFIG=tmpfs,/dev/ram1,overlay\n")
            host_config_data = self.host_config.render()
            if host_config_data:
                kiwi_config_file.write("{}\n".format(host_config_data.format(netboot_ip=self.netboot_ip)))
