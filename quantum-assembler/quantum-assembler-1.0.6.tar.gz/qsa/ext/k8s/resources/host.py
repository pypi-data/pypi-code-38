from qsa.lib.datastructures import DTO


class HostMixin:

    @staticmethod
    def parsenamedport(value):
        """Parse a named port from the format `<name>:<src>:<dst>`."""
        # This would look better in a class.
        if value.count(':') == 1:
            name, src = str.split(value, ':')
            dst = None
            protocol_port = src
        elif value.count(':') == 2:
            name, src, dst = str.split(value, ':')
            protocol_port = dst
        else:
            raise ValueError(f"Invalid port format: {value}")
        protocol = 'TCP'
        if '/' in protocol_port:
            protocol = str.upper(str.split(protocol_port, '/')[-1])
        return DTO(name=name, src=int(src.split('/')[0]),
            dst=int(dst.split('/')[0]) if dst else None, protocol=protocol)
