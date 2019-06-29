# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Fox(KaitaiStruct):
    """:field id: raw.hdr.id
    :field reset_count: raw.hdr.reset_count
    :field uptime: raw.hdr.uptime
    :field frm_type: raw.hdr.frm_type
    :field batt_a_v: raw.frame.rt_tlm.batt_a_v
    :field batt_b_v: raw.frame.rt_tlm.batt_b_v
    :field batt_c_v: raw.frame.rt_tlm.batt_c_v
    :field batt_a_t: raw.frame.rt_tlm.batt_a_t
    :field batt_b_t: raw.frame.rt_tlm.batt_b_t
    :field batt_c_t: raw.frame.rt_tlm.batt_c_t
    :field total_batt_i: raw.frame.rt_tlm.total_batt_i
    :field batt_board_temp: raw.frame.rt_tlm.batt_board_temp
    :field pos_x_panel_v: raw.frame.rt_tlm.pos_x_panel_v
    :field neg_x_panel_v: raw.frame.rt_tlm.neg_x_panel_v
    :field pos_y_panel_v: raw.frame.rt_tlm.pos_y_panel_v
    :field neg_y_panel_v: raw.frame.rt_tlm.neg_y_panel_v
    :field pos_z_panel_v: raw.frame.rt_tlm.pos_z_panel_v
    :field neg_z_panel_v: raw.frame.rt_tlm.neg_z_panel_v
    :field pos_x_panel_t: raw.frame.rt_tlm.pos_x_panel_t
    :field neg_x_panel_t: raw.frame.rt_tlm.neg_x_panel_t
    :field pos_y_panel_t: raw.frame.rt_tlm.pos_y_panel_t
    :field neg_y_panel_t: raw.frame.rt_tlm.neg_y_panel_t
    :field pos_z_panel_t: raw.frame.rt_tlm.pos_z_panel_t
    :field neg_z_panel_t: raw.frame.rt_tlm.neg_z_panel_t
    :field psu_temp: raw.frame.rt_tlm.psu_temp
    :field spin: raw.frame.rt_tlm.spin
    :field tx_pa_curr: raw.frame.rt_tlm.tx_pa_curr
    :field tx_temp: raw.frame.rt_tlm.tx_temp
    :field rx_temp: raw.frame.rt_tlm.rx_temp
    :field rssi: raw.frame.rt_tlm.rssi
    :field ihu_cpu_temp: raw.frame.rt_tlm.ihu_cpu_temp
    :field sat_x_ang_vcty: raw.frame.rt_tlm.sat_x_ang_vcty
    :field sat_y_ang_vcty: raw.frame.rt_tlm.sat_y_ang_vcty
    :field sat_z_ang_vcty: raw.frame.rt_tlm.sat_z_ang_vcty
    :field exp_4_temp: raw.frame.rt_tlm.exp_4_temp
    :field psu_curr: raw.frame.rt_tlm.psu_curr
    :field ihu_diag_data: raw.frame.rt_tlm.ihu_diag_data
    :field exp_fail_ind: raw.frame.rt_tlm.exp_fail_ind
    :field sys_i2c_fail_ind: raw.frame.rt_tlm.sys_i2c_fail_ind
    :field grnd_cmded_tlm_rsts: raw.frame.rt_tlm.grnd_cmded_tlm_rsts
    :field ant_deploy_sensors: raw.frame.rt_tlm.ant_deploy_sensors
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_raw = self._io.read_bytes_full()
        io = KaitaiStream(BytesIO(self._raw_raw))
        self.raw = self._root.Frame(io, self, self._root)

    class Hdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = [None] * (6)
            for i in range(6):
                self.b[i] = self._io.read_u1()


        @property
        def id(self):
            if hasattr(self, '_m_id'):
                return self._m_id if hasattr(self, '_m_id') else None

            self._m_id = (self.b[0] & 7)
            return self._m_id if hasattr(self, '_m_id') else None

        @property
        def reset_count(self):
            if hasattr(self, '_m_reset_count'):
                return self._m_reset_count if hasattr(self, '_m_reset_count') else None

            self._m_reset_count = (((((self.b[2] << 16) | (self.b[1] << 8)) | self.b[0]) >> 3) & 65535)
            return self._m_reset_count if hasattr(self, '_m_reset_count') else None

        @property
        def uptime(self):
            if hasattr(self, '_m_uptime'):
                return self._m_uptime if hasattr(self, '_m_uptime') else None

            self._m_uptime = ((((((self.b[5] << 24) | (self.b[4] << 16)) | (self.b[3] << 8)) | self.b[2]) >> 3) & 33554431)
            return self._m_uptime if hasattr(self, '_m_uptime') else None

        @property
        def frm_type(self):
            if hasattr(self, '_m_frm_type'):
                return self._m_frm_type if hasattr(self, '_m_frm_type') else None

            self._m_frm_type = ((self.b[5] >> 4) & 15)
            return self._m_frm_type if hasattr(self, '_m_frm_type') else None


    class MinValsTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.min_vals_tlm = self._root.MinValsTlm(self._io, self, self._root)


    class MinValsTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = []
            i = 0
            while not self._io.is_eof():
                self.b.append(self._io.read_u1())
                i += 1



    class RtTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = []
            i = 0
            while not self._io.is_eof():
                self.b.append(self._io.read_u1())
                i += 1


        @property
        def exp_4_temp(self):
            if hasattr(self, '_m_exp_4_temp'):
                return self._m_exp_4_temp if hasattr(self, '_m_exp_4_temp') else None

            self._m_exp_4_temp = (((self.b[46] & 15) << 8) | self.b[45])
            return self._m_exp_4_temp if hasattr(self, '_m_exp_4_temp') else None

        @property
        def total_batt_i(self):
            if hasattr(self, '_m_total_batt_i'):
                return self._m_total_batt_i if hasattr(self, '_m_total_batt_i') else None

            self._m_total_batt_i = (((self.b[10] & 15) << 8) | self.b[9])
            return self._m_total_batt_i if hasattr(self, '_m_total_batt_i') else None

        @property
        def rx_temp(self):
            if hasattr(self, '_m_rx_temp'):
                return self._m_rx_temp if hasattr(self, '_m_rx_temp') else None

            self._m_rx_temp = (((self.b[37] & 15) << 8) | self.b[36])
            return self._m_rx_temp if hasattr(self, '_m_rx_temp') else None

        @property
        def tx_pa_curr(self):
            if hasattr(self, '_m_tx_pa_curr'):
                return self._m_tx_pa_curr if hasattr(self, '_m_tx_pa_curr') else None

            self._m_tx_pa_curr = (((self.b[34] & 15) << 8) | self.b[33])
            return self._m_tx_pa_curr if hasattr(self, '_m_tx_pa_curr') else None

        @property
        def exp_fail_ind(self):
            if hasattr(self, '_m_exp_fail_ind'):
                return self._m_exp_fail_ind if hasattr(self, '_m_exp_fail_ind') else None

            self._m_exp_fail_ind = (self.b[52] & 15)
            return self._m_exp_fail_ind if hasattr(self, '_m_exp_fail_ind') else None

        @property
        def pos_x_panel_v(self):
            if hasattr(self, '_m_pos_x_panel_v'):
                return self._m_pos_x_panel_v if hasattr(self, '_m_pos_x_panel_v') else None

            self._m_pos_x_panel_v = (((self.b[13] & 15) << 8) | self.b[12])
            return self._m_pos_x_panel_v if hasattr(self, '_m_pos_x_panel_v') else None

        @property
        def batt_a_v(self):
            if hasattr(self, '_m_batt_a_v'):
                return self._m_batt_a_v if hasattr(self, '_m_batt_a_v') else None

            self._m_batt_a_v = (((self.b[1] & 15) << 8) | self.b[0])
            return self._m_batt_a_v if hasattr(self, '_m_batt_a_v') else None

        @property
        def sat_y_ang_vcty(self):
            if hasattr(self, '_m_sat_y_ang_vcty'):
                return self._m_sat_y_ang_vcty if hasattr(self, '_m_sat_y_ang_vcty') else None

            self._m_sat_y_ang_vcty = (((self.b[43] & 15) << 8) | self.b[42])
            return self._m_sat_y_ang_vcty if hasattr(self, '_m_sat_y_ang_vcty') else None

        @property
        def rssi(self):
            if hasattr(self, '_m_rssi'):
                return self._m_rssi if hasattr(self, '_m_rssi') else None

            self._m_rssi = ((self.b[38] << 4) | (self.b[37] >> 4))
            return self._m_rssi if hasattr(self, '_m_rssi') else None

        @property
        def pos_z_panel_t(self):
            if hasattr(self, '_m_pos_z_panel_t'):
                return self._m_pos_z_panel_t if hasattr(self, '_m_pos_z_panel_t') else None

            self._m_pos_z_panel_t = (((self.b[28] & 15) << 8) | self.b[27])
            return self._m_pos_z_panel_t if hasattr(self, '_m_pos_z_panel_t') else None

        @property
        def batt_a_t(self):
            if hasattr(self, '_m_batt_a_t'):
                return self._m_batt_a_t if hasattr(self, '_m_batt_a_t') else None

            self._m_batt_a_t = ((self.b[5] << 4) | (self.b[4] >> 4))
            return self._m_batt_a_t if hasattr(self, '_m_batt_a_t') else None

        @property
        def batt_c_v(self):
            if hasattr(self, '_m_batt_c_v'):
                return self._m_batt_c_v if hasattr(self, '_m_batt_c_v') else None

            self._m_batt_c_v = (((self.b[4] & 15) << 8) | self.b[3])
            return self._m_batt_c_v if hasattr(self, '_m_batt_c_v') else None

        @property
        def neg_z_panel_t(self):
            if hasattr(self, '_m_neg_z_panel_t'):
                return self._m_neg_z_panel_t if hasattr(self, '_m_neg_z_panel_t') else None

            self._m_neg_z_panel_t = ((self.b[29] << 4) | (self.b[28] >> 4))
            return self._m_neg_z_panel_t if hasattr(self, '_m_neg_z_panel_t') else None

        @property
        def ihu_diag_data(self):
            if hasattr(self, '_m_ihu_diag_data'):
                return self._m_ihu_diag_data if hasattr(self, '_m_ihu_diag_data') else None

            self._m_ihu_diag_data = ((((self.b[51] << 24) | (self.b[50] << 16)) | (self.b[49] << 8)) | self.b[48])
            return self._m_ihu_diag_data if hasattr(self, '_m_ihu_diag_data') else None

        @property
        def batt_board_temp(self):
            if hasattr(self, '_m_batt_board_temp'):
                return self._m_batt_board_temp if hasattr(self, '_m_batt_board_temp') else None

            self._m_batt_board_temp = ((self.b[11] << 4) | (self.b[10] >> 4))
            return self._m_batt_board_temp if hasattr(self, '_m_batt_board_temp') else None

        @property
        def pos_z_panel_v(self):
            if hasattr(self, '_m_pos_z_panel_v'):
                return self._m_pos_z_panel_v if hasattr(self, '_m_pos_z_panel_v') else None

            self._m_pos_z_panel_v = (((self.b[19] & 15) << 8) | self.b[18])
            return self._m_pos_z_panel_v if hasattr(self, '_m_pos_z_panel_v') else None

        @property
        def pos_y_panel_t(self):
            if hasattr(self, '_m_pos_y_panel_t'):
                return self._m_pos_y_panel_t if hasattr(self, '_m_pos_y_panel_t') else None

            self._m_pos_y_panel_t = (((self.b[25] & 15) << 8) | self.b[24])
            return self._m_pos_y_panel_t if hasattr(self, '_m_pos_y_panel_t') else None

        @property
        def ant_deploy_sensors(self):
            if hasattr(self, '_m_ant_deploy_sensors'):
                return self._m_ant_deploy_sensors if hasattr(self, '_m_ant_deploy_sensors') else None

            self._m_ant_deploy_sensors = ((self.b[53] >> 3) & 3)
            return self._m_ant_deploy_sensors if hasattr(self, '_m_ant_deploy_sensors') else None

        @property
        def psu_temp(self):
            if hasattr(self, '_m_psu_temp'):
                return self._m_psu_temp if hasattr(self, '_m_psu_temp') else None

            self._m_psu_temp = (((self.b[31] & 15) << 8) | self.b[30])
            return self._m_psu_temp if hasattr(self, '_m_psu_temp') else None

        @property
        def spin(self):
            if hasattr(self, '_m_spin'):
                return self._m_spin if hasattr(self, '_m_spin') else None

            self._m_spin = ((self.b[32] << 4) | (self.b[31] >> 4))
            return self._m_spin if hasattr(self, '_m_spin') else None

        @property
        def batt_b_t(self):
            if hasattr(self, '_m_batt_b_t'):
                return self._m_batt_b_t if hasattr(self, '_m_batt_b_t') else None

            self._m_batt_b_t = (((self.b[7] & 15) << 8) | self.b[6])
            return self._m_batt_b_t if hasattr(self, '_m_batt_b_t') else None

        @property
        def sat_x_ang_vcty(self):
            if hasattr(self, '_m_sat_x_ang_vcty'):
                return self._m_sat_x_ang_vcty if hasattr(self, '_m_sat_x_ang_vcty') else None

            self._m_sat_x_ang_vcty = ((self.b[41] << 4) | (self.b[40] >> 4))
            return self._m_sat_x_ang_vcty if hasattr(self, '_m_sat_x_ang_vcty') else None

        @property
        def neg_y_panel_t(self):
            if hasattr(self, '_m_neg_y_panel_t'):
                return self._m_neg_y_panel_t if hasattr(self, '_m_neg_y_panel_t') else None

            self._m_neg_y_panel_t = ((self.b[26] << 4) | (self.b[25] >> 4))
            return self._m_neg_y_panel_t if hasattr(self, '_m_neg_y_panel_t') else None

        @property
        def neg_y_panel_v(self):
            if hasattr(self, '_m_neg_y_panel_v'):
                return self._m_neg_y_panel_v if hasattr(self, '_m_neg_y_panel_v') else None

            self._m_neg_y_panel_v = ((self.b[17] << 4) | (self.b[16] >> 4))
            return self._m_neg_y_panel_v if hasattr(self, '_m_neg_y_panel_v') else None

        @property
        def pos_y_panel_v(self):
            if hasattr(self, '_m_pos_y_panel_v'):
                return self._m_pos_y_panel_v if hasattr(self, '_m_pos_y_panel_v') else None

            self._m_pos_y_panel_v = (((self.b[16] & 15) << 8) | self.b[15])
            return self._m_pos_y_panel_v if hasattr(self, '_m_pos_y_panel_v') else None

        @property
        def psu_curr(self):
            if hasattr(self, '_m_psu_curr'):
                return self._m_psu_curr if hasattr(self, '_m_psu_curr') else None

            self._m_psu_curr = ((self.b[47] << 4) | (self.b[46] >> 4))
            return self._m_psu_curr if hasattr(self, '_m_psu_curr') else None

        @property
        def ihu_cpu_temp(self):
            if hasattr(self, '_m_ihu_cpu_temp'):
                return self._m_ihu_cpu_temp if hasattr(self, '_m_ihu_cpu_temp') else None

            self._m_ihu_cpu_temp = (((self.b[40] & 15) << 8) | self.b[39])
            return self._m_ihu_cpu_temp if hasattr(self, '_m_ihu_cpu_temp') else None

        @property
        def grnd_cmded_tlm_rsts(self):
            if hasattr(self, '_m_grnd_cmded_tlm_rsts'):
                return self._m_grnd_cmded_tlm_rsts if hasattr(self, '_m_grnd_cmded_tlm_rsts') else None

            self._m_grnd_cmded_tlm_rsts = ((((self.b[52] >> 7) & 1) | (self.b[53] << 1)) & 15)
            return self._m_grnd_cmded_tlm_rsts if hasattr(self, '_m_grnd_cmded_tlm_rsts') else None

        @property
        def batt_b_v(self):
            if hasattr(self, '_m_batt_b_v'):
                return self._m_batt_b_v if hasattr(self, '_m_batt_b_v') else None

            self._m_batt_b_v = ((self.b[2] << 4) | (self.b[1] >> 4))
            return self._m_batt_b_v if hasattr(self, '_m_batt_b_v') else None

        @property
        def neg_x_panel_v(self):
            if hasattr(self, '_m_neg_x_panel_v'):
                return self._m_neg_x_panel_v if hasattr(self, '_m_neg_x_panel_v') else None

            self._m_neg_x_panel_v = ((self.b[14] << 4) | (self.b[13] >> 4))
            return self._m_neg_x_panel_v if hasattr(self, '_m_neg_x_panel_v') else None

        @property
        def pos_x_panel_t(self):
            if hasattr(self, '_m_pos_x_panel_t'):
                return self._m_pos_x_panel_t if hasattr(self, '_m_pos_x_panel_t') else None

            self._m_pos_x_panel_t = (((self.b[22] & 15) << 8) | self.b[21])
            return self._m_pos_x_panel_t if hasattr(self, '_m_pos_x_panel_t') else None

        @property
        def tx_temp(self):
            if hasattr(self, '_m_tx_temp'):
                return self._m_tx_temp if hasattr(self, '_m_tx_temp') else None

            self._m_tx_temp = ((self.b[35] << 4) | (self.b[34] >> 4))
            return self._m_tx_temp if hasattr(self, '_m_tx_temp') else None

        @property
        def neg_z_panel_v(self):
            if hasattr(self, '_m_neg_z_panel_v'):
                return self._m_neg_z_panel_v if hasattr(self, '_m_neg_z_panel_v') else None

            self._m_neg_z_panel_v = ((self.b[20] << 4) | (self.b[19] >> 4))
            return self._m_neg_z_panel_v if hasattr(self, '_m_neg_z_panel_v') else None

        @property
        def neg_x_panel_t(self):
            if hasattr(self, '_m_neg_x_panel_t'):
                return self._m_neg_x_panel_t if hasattr(self, '_m_neg_x_panel_t') else None

            self._m_neg_x_panel_t = ((self.b[23] << 4) | (self.b[22] >> 4))
            return self._m_neg_x_panel_t if hasattr(self, '_m_neg_x_panel_t') else None

        @property
        def batt_c_t(self):
            if hasattr(self, '_m_batt_c_t'):
                return self._m_batt_c_t if hasattr(self, '_m_batt_c_t') else None

            self._m_batt_c_t = ((self.b[8] << 4) | (self.b[7] >> 4))
            return self._m_batt_c_t if hasattr(self, '_m_batt_c_t') else None

        @property
        def sat_z_ang_vcty(self):
            if hasattr(self, '_m_sat_z_ang_vcty'):
                return self._m_sat_z_ang_vcty if hasattr(self, '_m_sat_z_ang_vcty') else None

            self._m_sat_z_ang_vcty = ((self.b[44] << 4) | (self.b[43] >> 4))
            return self._m_sat_z_ang_vcty if hasattr(self, '_m_sat_z_ang_vcty') else None

        @property
        def sys_i2c_fail_ind(self):
            if hasattr(self, '_m_sys_i2c_fail_ind'):
                return self._m_sys_i2c_fail_ind if hasattr(self, '_m_sys_i2c_fail_ind') else None

            self._m_sys_i2c_fail_ind = ((self.b[52] >> 4) & 7)
            return self._m_sys_i2c_fail_ind if hasattr(self, '_m_sys_i2c_fail_ind') else None


    class ExpTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.exp_tlm = self._io.read_bytes_full()


    class MaxValsTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b = []
            i = 0
            while not self._io.is_eof():
                self.b.append(self._io.read_u1())
                i += 1



    class MaxValsTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.max_vals_tlm = self._root.MaxValsTlm(self._io, self, self._root)


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_hdr = self._io.read_bytes(6)
            io = KaitaiStream(BytesIO(self._raw_hdr))
            self.hdr = self._root.Hdr(io, self, self._root)
            _on = self.hdr.frm_type
            if _on == 0:
                self.frame = self._root.DebugDataT(self._io, self, self._root)
            elif _on == 4:
                self.frame = self._root.ExpTlmT(self._io, self, self._root)
            elif _on == 1:
                self.frame = self._root.RtTlmT(self._io, self, self._root)
            elif _on == 3:
                self.frame = self._root.MinValsTlmT(self._io, self, self._root)
            elif _on == 5:
                self.frame = self._root.CamJpegDataT(self._io, self, self._root)
            elif _on == 2:
                self.frame = self._root.MaxValsTlmT(self._io, self, self._root)


    class CamJpegDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cam_jpeg_data = self._io.read_bytes_full()


    class RtTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rt_tlm = self._root.RtTlm(self._io, self, self._root)


    class DebugDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.debug_data = self._io.read_bytes_full()



