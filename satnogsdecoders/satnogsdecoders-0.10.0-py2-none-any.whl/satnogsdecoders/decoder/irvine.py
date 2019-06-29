# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Irvine(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field spacecraft_response: ax25_frame.payload.ax25_info.body.body.spacecraft_response
    :field spacecraft_id: ax25_frame.payload.ax25_info.body.body.spacecraft_id
    :field ldc: ax25_frame.payload.ax25_info.body.body.ldc
    :field gyro: ax25_frame.payload.ax25_info.body.body.gyro
    :field mag: ax25_frame.payload.ax25_info.body.body.mag
    :field daughter_a_tmp_sensor: ax25_frame.payload.ax25_info.body.body.daughter_a_tmp_sensor
    :field three_v_pl_tmp_sensor: ax25_frame.payload.ax25_info.body.body.three_v_pl_tmp_sensor
    :field temp_nz: ax25_frame.payload.ax25_info.body.body.temp_nz
    :field volt3v: ax25_frame.payload.ax25_info.body.body.volt3v
    :field curr3v: ax25_frame.payload.ax25_info.body.body.curr3v
    :field volt5vpl: ax25_frame.payload.ax25_info.body.body.volt5vpl
    :field curr5vpl: ax25_frame.payload.ax25_info.body.body.curr5vpl
    :field src_port: ax25_frame.payload.ax25_info.body.body.src_port
    :field dst_port: ax25_frame.payload.ax25_info.body.body.dst_port
    :field src_ip_addr: ax25_frame.payload.ax25_info.src_ip_addr
    :field dst_ip_addr: ax25_frame.payload.ax25_info.dst_ip_addr
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = self._root.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = self._root.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = self._root.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = self._root.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = self._root.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = self._root.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = self._root.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = self._root.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = self._root.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = self._root.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = self._root.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = self._root.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self.pid
            if _on == 204:
                self._raw_ax25_info = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = self._root.Ipv4Pkt(io, self, self._root)
            elif _on == 240:
                self._raw_ax25_info = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = self._root.NoneL3(io, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class UdpPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.spacecraft_response = self._io.read_u1()
            self.spacecraft_id = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self.ldc = self._io.read_u2be()
            self.gyro = [None] * (3)
            for i in range(3):
                self.gyro[i] = self._io.read_s4be()

            self.mag = [None] * (3)
            for i in range(3):
                self.mag[i] = self._io.read_s4be()

            self.daughter_a_tmp_sensor = self._io.read_s2be()
            self.three_v_pl_tmp_sensor = self._io.read_s2be()
            self.temp_nz = self._io.read_s2be()
            self.volt3v = self._io.read_s4be()
            self.curr3v = self._io.read_s4be()
            self.volt5vpl = self._io.read_s4be()
            self.curr5vpl = self._io.read_s4be()

        @property
        def gyro_y(self):
            if hasattr(self, '_m_gyro_y'):
                return self._m_gyro_y if hasattr(self, '_m_gyro_y') else None

            self._m_gyro_y = (self.gyro[1] / (1024.0 * 1024.0))
            return self._m_gyro_y if hasattr(self, '_m_gyro_y') else None

        @property
        def three_v_pl_tmp_sensor_val_k(self):
            if hasattr(self, '_m_three_v_pl_tmp_sensor_val_k'):
                return self._m_three_v_pl_tmp_sensor_val_k if hasattr(self, '_m_three_v_pl_tmp_sensor_val_k') else None

            self._m_three_v_pl_tmp_sensor_val_k = (self.three_v_pl_tmp_sensor / 64.0)
            return self._m_three_v_pl_tmp_sensor_val_k if hasattr(self, '_m_three_v_pl_tmp_sensor_val_k') else None

        @property
        def curr3v_val(self):
            if hasattr(self, '_m_curr3v_val'):
                return self._m_curr3v_val if hasattr(self, '_m_curr3v_val') else None

            self._m_curr3v_val = (self.curr3v / (256.0 * 256.0))
            return self._m_curr3v_val if hasattr(self, '_m_curr3v_val') else None

        @property
        def ldc_hrs(self):
            if hasattr(self, '_m_ldc_hrs'):
                return self._m_ldc_hrs if hasattr(self, '_m_ldc_hrs') else None

            self._m_ldc_hrs = (self.ldc_mins / 60.0)
            return self._m_ldc_hrs if hasattr(self, '_m_ldc_hrs') else None

        @property
        def mag_z(self):
            """Magnitudes in [nT]!."""
            if hasattr(self, '_m_mag_z'):
                return self._m_mag_z if hasattr(self, '_m_mag_z') else None

            self._m_mag_z = (self.mag[2] / (1024.0 * 1024.0))
            return self._m_mag_z if hasattr(self, '_m_mag_z') else None

        @property
        def gyro_x(self):
            if hasattr(self, '_m_gyro_x'):
                return self._m_gyro_x if hasattr(self, '_m_gyro_x') else None

            self._m_gyro_x = (self.gyro[0] / (1024.0 * 1024.0))
            return self._m_gyro_x if hasattr(self, '_m_gyro_x') else None

        @property
        def ldc_secs(self):
            if hasattr(self, '_m_ldc_secs'):
                return self._m_ldc_secs if hasattr(self, '_m_ldc_secs') else None

            self._m_ldc_secs = (self.ldc * 256.0)
            return self._m_ldc_secs if hasattr(self, '_m_ldc_secs') else None

        @property
        def gyro_z(self):
            """Gyroscope in [deg/s]!."""
            if hasattr(self, '_m_gyro_z'):
                return self._m_gyro_z if hasattr(self, '_m_gyro_z') else None

            self._m_gyro_z = (self.gyro[2] / (1024.0 * 1024.0))
            return self._m_gyro_z if hasattr(self, '_m_gyro_z') else None

        @property
        def curr5vpl_val(self):
            """Voltages in [V]! Currents in [A]!
            IRVINE payload inside a UDP datagram multicast packet
            Currently partially reverse-engineered
            Conversion values taken from source-code
            """
            if hasattr(self, '_m_curr5vpl_val'):
                return self._m_curr5vpl_val if hasattr(self, '_m_curr5vpl_val') else None

            self._m_curr5vpl_val = (self.curr5vpl / (256.0 * 256.0))
            return self._m_curr5vpl_val if hasattr(self, '_m_curr5vpl_val') else None

        @property
        def three_v_pl_tmp_sensor_val_deg_c(self):
            if hasattr(self, '_m_three_v_pl_tmp_sensor_val_deg_c'):
                return self._m_three_v_pl_tmp_sensor_val_deg_c if hasattr(self, '_m_three_v_pl_tmp_sensor_val_deg_c') else None

            self._m_three_v_pl_tmp_sensor_val_deg_c = (self.three_v_pl_tmp_sensor_val_k - 273.15)
            return self._m_three_v_pl_tmp_sensor_val_deg_c if hasattr(self, '_m_three_v_pl_tmp_sensor_val_deg_c') else None

        @property
        def mag_x(self):
            if hasattr(self, '_m_mag_x'):
                return self._m_mag_x if hasattr(self, '_m_mag_x') else None

            self._m_mag_x = (self.mag[0] / (1024.0 * 1024.0))
            return self._m_mag_x if hasattr(self, '_m_mag_x') else None

        @property
        def volt5vpl_val(self):
            if hasattr(self, '_m_volt5vpl_val'):
                return self._m_volt5vpl_val if hasattr(self, '_m_volt5vpl_val') else None

            self._m_volt5vpl_val = (self.volt5vpl / (256.0 * 256.0))
            return self._m_volt5vpl_val if hasattr(self, '_m_volt5vpl_val') else None

        @property
        def temp_nz_val_k(self):
            """Temperatures in [K]!."""
            if hasattr(self, '_m_temp_nz_val_k'):
                return self._m_temp_nz_val_k if hasattr(self, '_m_temp_nz_val_k') else None

            self._m_temp_nz_val_k = (self.temp_nz / 64.0)
            return self._m_temp_nz_val_k if hasattr(self, '_m_temp_nz_val_k') else None

        @property
        def daughter_a_tmp_sensor_val_k(self):
            if hasattr(self, '_m_daughter_a_tmp_sensor_val_k'):
                return self._m_daughter_a_tmp_sensor_val_k if hasattr(self, '_m_daughter_a_tmp_sensor_val_k') else None

            self._m_daughter_a_tmp_sensor_val_k = (self.daughter_a_tmp_sensor / 64.0)
            return self._m_daughter_a_tmp_sensor_val_k if hasattr(self, '_m_daughter_a_tmp_sensor_val_k') else None

        @property
        def daughter_a_tmp_sensor_val_deg_c(self):
            if hasattr(self, '_m_daughter_a_tmp_sensor_val_deg_c'):
                return self._m_daughter_a_tmp_sensor_val_deg_c if hasattr(self, '_m_daughter_a_tmp_sensor_val_deg_c') else None

            self._m_daughter_a_tmp_sensor_val_deg_c = (self.daughter_a_tmp_sensor_val_k - 273.15)
            return self._m_daughter_a_tmp_sensor_val_deg_c if hasattr(self, '_m_daughter_a_tmp_sensor_val_deg_c') else None

        @property
        def mag_y(self):
            if hasattr(self, '_m_mag_y'):
                return self._m_mag_y if hasattr(self, '_m_mag_y') else None

            self._m_mag_y = (self.mag[1] / (1024.0 * 1024.0))
            return self._m_mag_y if hasattr(self, '_m_mag_y') else None

        @property
        def ldc_mins(self):
            if hasattr(self, '_m_ldc_mins'):
                return self._m_ldc_mins if hasattr(self, '_m_ldc_mins') else None

            self._m_ldc_mins = (self.ldc_secs / 60.0)
            return self._m_ldc_mins if hasattr(self, '_m_ldc_mins') else None

        @property
        def volt3v_val(self):
            if hasattr(self, '_m_volt3v_val'):
                return self._m_volt3v_val if hasattr(self, '_m_volt3v_val') else None

            self._m_volt3v_val = (self.volt3v / (256.0 * 256.0))
            return self._m_volt3v_val if hasattr(self, '_m_volt3v_val') else None

        @property
        def temp_nz_val_deg_c(self):
            """Temperatures in [C]!."""
            if hasattr(self, '_m_temp_nz_val_deg_c'):
                return self._m_temp_nz_val_deg_c if hasattr(self, '_m_temp_nz_val_deg_c') else None

            self._m_temp_nz_val_deg_c = (self.temp_nz_val_k - 273.15)
            return self._m_temp_nz_val_deg_c if hasattr(self, '_m_temp_nz_val_deg_c') else None


    class Ipv4Options(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while not self._io.is_eof():
                self.entries.append(self._root.Ipv4Option(self._io, self, self._root))
                i += 1



    class NoNextHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass


    class Ipv6Pkt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_bits_int(4)
            self.traffic_class = self._io.read_bits_int(8)
            self.flow_label = self._io.read_bits_int(20)
            self._io.align_to_byte()
            self.payload_length = self._io.read_u2be()
            self.next_header_type = self._io.read_u1()
            self.hop_limit = self._io.read_u1()
            self.src_ipv6_addr = self._io.read_bytes(16)
            self.dst_ipv6_addr = self._io.read_bytes(16)
            _on = self.next_header_type
            if _on == 17:
                self.next_header = self._root.UdpDtgrm(self._io, self, self._root)
            elif _on == 0:
                self.next_header = self._root.OptionHopByHop(self._io, self, self._root)
            elif _on == 4:
                self.next_header = self._root.Ipv4Pkt(self._io, self, self._root)
            elif _on == 6:
                self.next_header = self._root.TcpSegm(self._io, self, self._root)
            elif _on == 59:
                self.next_header = self._root.NoNextHeader(self._io, self, self._root)
            self.rest = self._io.read_bytes_full()


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class SsidMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ssid_mask = self._io.read_u1()

        @property
        def ssid(self):
            if hasattr(self, '_m_ssid'):
                return self._m_ssid if hasattr(self, '_m_ssid') else None

            self._m_ssid = ((self.ssid_mask & 15) >> 1)
            return self._m_ssid if hasattr(self, '_m_ssid') else None


    class Ipv4Pkt(KaitaiStruct):

        class ProtocolEnum(Enum):
            hopopt = 0
            icmp = 1
            igmp = 2
            ggp = 3
            ipv4 = 4
            st = 5
            tcp = 6
            cbt = 7
            egp = 8
            igp = 9
            bbn_rcc_mon = 10
            nvp_ii = 11
            pup = 12
            argus = 13
            emcon = 14
            xnet = 15
            chaos = 16
            udp = 17
            mux = 18
            dcn_meas = 19
            hmp = 20
            prm = 21
            xns_idp = 22
            trunk_1 = 23
            trunk_2 = 24
            leaf_1 = 25
            leaf_2 = 26
            rdp = 27
            irtp = 28
            iso_tp4 = 29
            netblt = 30
            mfe_nsp = 31
            merit_inp = 32
            dccp = 33
            x_3pc = 34
            idpr = 35
            xtp = 36
            ddp = 37
            idpr_cmtp = 38
            tp_plus_plus = 39
            il = 40
            ipv6 = 41
            sdrp = 42
            ipv6_route = 43
            ipv6_frag = 44
            idrp = 45
            rsvp = 46
            gre = 47
            dsr = 48
            bna = 49
            esp = 50
            ah = 51
            i_nlsp = 52
            swipe = 53
            narp = 54
            mobile = 55
            tlsp = 56
            skip = 57
            ipv6_icmp = 58
            ipv6_nonxt = 59
            ipv6_opts = 60
            any_host_internal_protocol = 61
            cftp = 62
            any_local_network = 63
            sat_expak = 64
            kryptolan = 65
            rvd = 66
            ippc = 67
            any_distributed_file_system = 68
            sat_mon = 69
            visa = 70
            ipcv = 71
            cpnx = 72
            cphb = 73
            wsn = 74
            pvp = 75
            br_sat_mon = 76
            sun_nd = 77
            wb_mon = 78
            wb_expak = 79
            iso_ip = 80
            vmtp = 81
            secure_vmtp = 82
            vines = 83
            ttp = 84
            nsfnet_igp = 85
            dgp = 86
            tcf = 87
            eigrp = 88
            ospfigp = 89
            sprite_rpc = 90
            larp = 91
            mtp = 92
            ax_25 = 93
            ipip = 94
            micp = 95
            scc_sp = 96
            etherip = 97
            encap = 98
            any_private_encryption_scheme = 99
            gmtp = 100
            ifmp = 101
            pnni = 102
            pim = 103
            aris = 104
            scps = 105
            qnx = 106
            a_n = 107
            ipcomp = 108
            snp = 109
            compaq_peer = 110
            ipx_in_ip = 111
            vrrp = 112
            pgm = 113
            any_0_hop = 114
            l2tp = 115
            ddx = 116
            iatp = 117
            stp = 118
            srp = 119
            uti = 120
            smp = 121
            sm = 122
            ptp = 123
            isis_over_ipv4 = 124
            fire = 125
            crtp = 126
            crudp = 127
            sscopmce = 128
            iplt = 129
            sps = 130
            pipe = 131
            sctp = 132
            fc = 133
            rsvp_e2e_ignore = 134
            mobility_header = 135
            udplite = 136
            mpls_in_ip = 137
            manet = 138
            hip = 139
            shim6 = 140
            wesp = 141
            rohc = 142
            reserved_255 = 255
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b1 = self._io.read_u1()
            self.b2 = self._io.read_u1()
            self.total_length = self._io.read_u2be()
            self.identification = self._io.read_u2be()
            self.b67 = self._io.read_u2be()
            self.ttl = self._io.read_u1()
            self.protocol = self._root.Ipv4Pkt.ProtocolEnum(self._io.read_u1())
            self.header_checksum = self._io.read_u2be()
            self.src_ip_addr = self._io.read_bytes(4)
            self.dst_ip_addr = self._io.read_bytes(4)
            self._raw_options = self._io.read_bytes((self.ihl_bytes - 20))
            io = KaitaiStream(BytesIO(self._raw_options))
            self.options = self._root.Ipv4Options(io, self, self._root)
            _on = self.protocol
            if _on == self._root.Ipv4Pkt.ProtocolEnum.tcp:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                io = KaitaiStream(BytesIO(self._raw_body))
                self.body = self._root.TcpSegm(io, self, self._root)
            elif _on == self._root.Ipv4Pkt.ProtocolEnum.icmp:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                io = KaitaiStream(BytesIO(self._raw_body))
                self.body = self._root.IcmpPkt(io, self, self._root)
            elif _on == self._root.Ipv4Pkt.ProtocolEnum.udp:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                io = KaitaiStream(BytesIO(self._raw_body))
                self.body = self._root.UdpDtgrm(io, self, self._root)
            elif _on == self._root.Ipv4Pkt.ProtocolEnum.ipv6:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                io = KaitaiStream(BytesIO(self._raw_body))
                self.body = self._root.Ipv6Pkt(io, self, self._root)
            else:
                self.body = self._io.read_bytes((self.total_length - self.ihl_bytes))

        @property
        def version(self):
            if hasattr(self, '_m_version'):
                return self._m_version if hasattr(self, '_m_version') else None

            self._m_version = ((self.b1 & 240) >> 4)
            return self._m_version if hasattr(self, '_m_version') else None

        @property
        def ihl(self):
            if hasattr(self, '_m_ihl'):
                return self._m_ihl if hasattr(self, '_m_ihl') else None

            self._m_ihl = (self.b1 & 15)
            return self._m_ihl if hasattr(self, '_m_ihl') else None

        @property
        def ihl_bytes(self):
            if hasattr(self, '_m_ihl_bytes'):
                return self._m_ihl_bytes if hasattr(self, '_m_ihl_bytes') else None

            self._m_ihl_bytes = (self.ihl * 4)
            return self._m_ihl_bytes if hasattr(self, '_m_ihl_bytes') else None


    class TcpSegm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.src_port = self._io.read_u2be()
            self.dst_port = self._io.read_u2be()
            self.seq_num = self._io.read_u4be()
            self.ack_num = self._io.read_u4be()
            self.b12 = self._io.read_u1()
            self.b13 = self._io.read_u1()
            self.window_size = self._io.read_u2be()
            self.checksum = self._io.read_u2be()
            self.urgent_pointer = self._io.read_u2be()
            self.body = self._io.read_bytes_full()


    class NoneL3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes_full()


    class UdpDtgrm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.src_port = self._io.read_u2be()
            self.dst_port = self._io.read_u2be()
            self.length = self._io.read_u2be()
            self.checksum = self._io.read_u2be()
            self._raw_body = self._io.read_bytes_full()
            io = KaitaiStream(BytesIO(self._raw_body))
            self.body = self._root.UdpPayload(io, self, self._root)


    class DestinationUnreachableMsg(KaitaiStruct):

        class DestinationUnreachableCode(Enum):
            net_unreachable = 0
            host_unreachable = 1
            protocol_unreachable = 2
            port_unreachable = 3
            fragmentation_needed_and_df_set = 4
            source_route_failed = 5
            dst_net_unkown = 6
            sdt_host_unkown = 7
            src_isolated = 8
            net_prohibited_by_admin = 9
            host_prohibited_by_admin = 10
            net_unreachable_for_tos = 11
            host_unreachable_for_tos = 12
            communication_prohibited_by_admin = 13
            host_precedence_violation = 14
            precedence_cuttoff_in_effect = 15
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = self._root.DestinationUnreachableMsg.DestinationUnreachableCode(self._io.read_u1())
            self.checksum = self._io.read_u2be()


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
            io = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = self._root.Callsign(io, self, self._root)


    class OptionHopByHop(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.next_header_type = self._io.read_u1()
            self.hdr_ext_len = self._io.read_u1()
            self.body = self._io.read_bytes((self.hdr_ext_len - 1))
            _on = self.next_header_type
            if _on == 0:
                self.next_header = self._root.OptionHopByHop(self._io, self, self._root)
            elif _on == 6:
                self.next_header = self._root.TcpSegm(self._io, self, self._root)
            elif _on == 59:
                self.next_header = self._root.NoNextHeader(self._io, self, self._root)


    class EchoMsg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = self._io.ensure_fixed_contents(b"\x00")
            self.checksum = self._io.read_u2be()
            self.identifier = self._io.read_u2be()
            self.seq_num = self._io.read_u2be()
            self.data = self._io.read_bytes_full()


    class TimeExceededMsg(KaitaiStruct):

        class TimeExceededCode(Enum):
            time_to_live_exceeded_in_transit = 0
            fragment_reassembly_time_exceeded = 1
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = self._root.TimeExceededMsg.TimeExceededCode(self._io.read_u1())
            self.checksum = self._io.read_u2be()


    class IcmpPkt(KaitaiStruct):

        class IcmpTypeEnum(Enum):
            echo_reply = 0
            destination_unreachable = 3
            source_quench = 4
            redirect = 5
            echo = 8
            time_exceeded = 11
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.icmp_type = self._root.IcmpPkt.IcmpTypeEnum(self._io.read_u1())
            if self.icmp_type == self._root.IcmpPkt.IcmpTypeEnum.destination_unreachable:
                self.destination_unreachable = self._root.DestinationUnreachableMsg(self._io, self, self._root)

            if self.icmp_type == self._root.IcmpPkt.IcmpTypeEnum.time_exceeded:
                self.time_exceeded = self._root.TimeExceededMsg(self._io, self, self._root)

            if  ((self.icmp_type == self._root.IcmpPkt.IcmpTypeEnum.echo) or (self.icmp_type == self._root.IcmpPkt.IcmpTypeEnum.echo_reply)) :
                self.echo = self._root.EchoMsg(self._io, self, self._root)



    class Ipv4Option(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b1 = self._io.read_u1()
            self.len = self._io.read_u1()
            self.body = self._io.read_bytes(((self.len - 2) if self.len > 2 else 0))

        @property
        def copy(self):
            if hasattr(self, '_m_copy'):
                return self._m_copy if hasattr(self, '_m_copy') else None

            self._m_copy = ((self.b1 & 128) >> 7)
            return self._m_copy if hasattr(self, '_m_copy') else None

        @property
        def opt_class(self):
            if hasattr(self, '_m_opt_class'):
                return self._m_opt_class if hasattr(self, '_m_opt_class') else None

            self._m_opt_class = ((self.b1 & 96) >> 5)
            return self._m_opt_class if hasattr(self, '_m_opt_class') else None

        @property
        def number(self):
            if hasattr(self, '_m_number'):
                return self._m_number if hasattr(self, '_m_number') else None

            self._m_number = (self.b1 & 31)
            return self._m_number if hasattr(self, '_m_number') else None



