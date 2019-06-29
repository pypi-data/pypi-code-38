# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Pwsat2(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field apid: ax25_frame.payload.ax25_info.hdr.apid
    :field periodic_msg_data: ax25_frame.payload.ax25_info.payload.periodic_msg_data
    :field obc_boot_ctr: ax25_frame.payload.ax25_info.payload.obc.obc_boot_ctr
    :field obc_boot_idx: ax25_frame.payload.ax25_info.payload.obc.obc_boot_idx
    :field obc_reboot_reason: ax25_frame.payload.ax25_info.payload.obc.obc_reboot_reason
    :field obc_code_crc: ax25_frame.payload.ax25_info.payload.obc.obc_code_crc
    :field obc_mission_time: ax25_frame.payload.ax25_info.payload.obc.obc_mission_time
    :field obc_ext_time: ax25_frame.payload.ax25_info.payload.obc.obc_ext_time
    :field obc_comm_err: ax25_frame.payload.ax25_info.payload.obc.obc_comm_err
    :field obc_eps_err: ax25_frame.payload.ax25_info.payload.obc.obc_eps_err
    :field obc_rtc_err: ax25_frame.payload.ax25_info.payload.obc.obc_rtc_err
    :field obc_imtq_err: ax25_frame.payload.ax25_info.payload.obc.obc_imtq_err
    :field obc_n25qflash1_err: ax25_frame.payload.ax25_info.payload.obc.obc_n25qflash1_err
    :field obc_n25qflash2_err: ax25_frame.payload.ax25_info.payload.obc.obc_n25qflash2_err
    :field obc_n25qflash3_err: ax25_frame.payload.ax25_info.payload.obc.obc_n25qflash3_err
    :field obc_n25q_tmr_corr: ax25_frame.payload.ax25_info.payload.obc.obc_n25q_tmr_corr
    :field obc_fram_tmr_corr: ax25_frame.payload.ax25_info.payload.obc.obc_fram_tmr_corr
    :field obc_payload_err: ax25_frame.payload.ax25_info.payload.obc.obc_payload_err
    :field obc_cam_err: ax25_frame.payload.ax25_info.payload.obc.obc_cam_err
    :field obc_suns_exp_err: ax25_frame.payload.ax25_info.payload.obc.obc_suns_exp_err
    :field obc_ant_prim_err: ax25_frame.payload.ax25_info.payload.obc.obc_ant_prim_err
    :field obc_ant_sec_err: ax25_frame.payload.ax25_info.payload.obc.obc_ant_sec_err
    :field obc_prim_flash_scrbg_ptr: ax25_frame.payload.ax25_info.payload.obc.obc_prim_flash_scrbg_ptr
    :field obc_sec_flash_scrbg_ptr: ax25_frame.payload.ax25_info.payload.obc.obc_sec_flash_scrbg_ptr
    :field obc_ram_scrbg_ptr: ax25_frame.payload.ax25_info.payload.obc.obc_ram_scrbg_ptr
    :field obc_system_uptime: ax25_frame.payload.ax25_info.payload.obc.obc_system_uptime
    :field obc_system_flash_free: ax25_frame.payload.ax25_info.payload.obc.obc_system_flash_free
    :field antennas_ant1_depl_sw_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_depl_sw_ch_a
    :field antennas_ant2_depl_sw_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_depl_sw_ch_a
    :field antennas_ant3_depl_sw_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_depl_sw_ch_a
    :field antennas_ant4_depl_sw_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_depl_sw_ch_a
    :field antennas_ant1_depl_sw_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_depl_sw_ch_b
    :field antennas_ant2_depl_sw_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_depl_sw_ch_b
    :field antennas_ant3_depl_sw_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_depl_sw_ch_b
    :field antennas_ant4_depl_sw_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_depl_sw_ch_b
    :field antennas_ant1_last_timed_stop_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_last_timed_stop_ch_a
    :field antennas_ant2_last_timed_stop_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_last_timed_stop_ch_a
    :field antennas_ant3_last_timed_stop_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_last_timed_stop_ch_a
    :field antennas_ant4_last_timed_stop_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_last_timed_stop_ch_a
    :field antennas_ant1_last_timed_stop_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_last_timed_stop_ch_b
    :field antennas_ant2_last_timed_stop_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_last_timed_stop_ch_b
    :field antennas_ant3_last_timed_stop_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_last_timed_stop_ch_b
    :field antennas_ant4_last_timed_stop_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_last_timed_stop_ch_b
    :field antennas_ant1_burn_active_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_burn_active_ch_a
    :field antennas_ant2_burn_active_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_burn_active_ch_a
    :field antennas_ant3_burn_active_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_burn_active_ch_a
    :field antennas_ant4_burn_active_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_burn_active_ch_a
    :field antennas_ant1_burn_active_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_burn_active_ch_b
    :field antennas_ant2_burn_active_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_burn_active_ch_b
    :field antennas_ant3_burn_active_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_burn_active_ch_b
    :field antennas_ant4_burn_active_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_burn_active_ch_b
    :field antennas_sys_indep_burn_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_sys_indep_burn_ch_a
    :field antennas_sys_indep_burn_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_sys_indep_burn_ch_b
    :field antennas_ant_ignoring_sw_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant_ignoring_sw_ch_a
    :field antennas_ant_ignoring_sw_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant_ignoring_sw_ch_b
    :field antennas_armed_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_armed_ch_a
    :field antennas_armed_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_armed_ch_b
    :field antennas_ant1_activation_cnt_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_activation_cnt_ch_a
    :field antennas_ant2_activation_cnt_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_activation_cnt_ch_a
    :field antennas_ant3_activation_cnt_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_activation_cnt_ch_a
    :field antennas_ant4_activation_cnt_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_activation_cnt_ch_a
    :field antennas_ant1_activation_cnt_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_activation_cnt_ch_b
    :field antennas_ant2_activation_cnt_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_activation_cnt_ch_b
    :field antennas_ant3_activation_cnt_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_activation_cnt_ch_b
    :field antennas_ant4_activation_cnt_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_activation_cnt_ch_b
    :field antennas_ant1_activation_time_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_activation_time_ch_a
    :field antennas_ant2_activation_time_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_activation_time_ch_a
    :field antennas_ant3_activation_time_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_activation_time_ch_a
    :field antennas_ant4_activation_time_ch_a: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_activation_time_ch_a
    :field antennas_ant1_activation_time_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant1_activation_time_ch_b
    :field antennas_ant2_activation_time_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant2_activation_time_ch_b
    :field antennas_ant3_activation_time_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant3_activation_time_ch_b
    :field antennas_ant4_activation_time_ch_b: ax25_frame.payload.ax25_info.payload.antennas.antennas_ant4_activation_time_ch_b
    :field experiments_curr_exp_code: ax25_frame.payload.ax25_info.payload.experiments.experiments_curr_exp_code
    :field experiments_exp_startup_res: ax25_frame.payload.ax25_info.payload.experiments.experiments_exp_startup_res
    :field experiments_last_exp_iter_stat_status: ax25_frame.payload.ax25_info.payload.experiments.experiments_last_exp_iter_stat_status
    :field gyroscope_x_meas: ax25_frame.payload.ax25_info.payload.gyroscope.gyroscope_x_meas
    :field gyroscope_y_meas: ax25_frame.payload.ax25_info.payload.gyroscope.gyroscope_y_meas
    :field gyroscope_z_meas: ax25_frame.payload.ax25_info.payload.gyroscope.gyroscope_z_meas
    :field gyroscope_temp: ax25_frame.payload.ax25_info.payload.gyroscope.gyroscope_temp
    :field comm_tx_trsmtr_uptime: ax25_frame.payload.ax25_info.payload.comm.comm_tx_trsmtr_uptime
    :field comm_tx_bitrate: ax25_frame.payload.ax25_info.payload.comm.comm_tx_bitrate
    :field comm_tx_last_tx_rf_refl_pwr: ax25_frame.payload.ax25_info.payload.comm.comm_tx_last_tx_rf_refl_pwr
    :field comm_tx_last_tx_pamp_temp: ax25_frame.payload.ax25_info.payload.comm.comm_tx_last_tx_pamp_temp
    :field comm_tx_last_tx_last_tx_rf_fwd_pwr: ax25_frame.payload.ax25_info.payload.comm.comm_tx_last_tx_last_tx_rf_fwd_pwr
    :field comm_tx_last_tx_curr_consmpt: ax25_frame.payload.ax25_info.payload.comm.comm_tx_last_tx_curr_consmpt
    :field comm_tx_now_tx_fwd_pwr: ax25_frame.payload.ax25_info.payload.comm.comm_tx_now_tx_fwd_pwr
    :field comm_tx_now_tx_curr_consmpt: ax25_frame.payload.ax25_info.payload.comm.comm_tx_now_tx_curr_consmpt
    :field comm_tx_state_when_idle: ax25_frame.payload.ax25_info.payload.comm.comm_tx_state_when_idle
    :field comm_tx_beacon_state: ax25_frame.payload.ax25_info.payload.comm.comm_tx_beacon_state
    :field comm_rx_uptime: ax25_frame.payload.ax25_info.payload.comm.comm_rx_uptime
    :field comm_rx_last_rx_doppler_offs: ax25_frame.payload.ax25_info.payload.comm.comm_rx_last_rx_doppler_offs
    :field comm_rx_last_rx_rssi: ax25_frame.payload.ax25_info.payload.comm.comm_rx_last_rx_rssi
    :field comm_rx_now_doppler_offs: ax25_frame.payload.ax25_info.payload.comm.comm_rx_now_doppler_offs
    :field comm_rx_now_rx_curr_consmpt: ax25_frame.payload.ax25_info.payload.comm.comm_rx_now_rx_curr_consmpt
    :field comm_rx_supply_voltage: ax25_frame.payload.ax25_info.payload.comm.comm_rx_supply_voltage
    :field comm_rx_osc_temp: ax25_frame.payload.ax25_info.payload.comm.comm_rx_osc_temp
    :field comm_rx_now_pamp_temp: ax25_frame.payload.ax25_info.payload.comm.comm_rx_now_pamp_temp
    :field comm_rx_now_rssi: ax25_frame.payload.ax25_info.payload.comm.comm_rx_now_rssi
    :field hardware_state_gpio_sail_deployed: ax25_frame.payload.ax25_info.payload.hardware_state.hardware_state_gpio_sail_deployed
    :field hardware_state_mcu_temp: ax25_frame.payload.ax25_info.payload.hardware_state.hardware_state_mcu_temp
    :field eps_controller_a_mpptx_sol_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mpptx_sol_volt
    :field eps_controller_a_mpptx_sol_curr: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mpptx_sol_curr
    :field eps_controller_a_mpptx_out_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mpptx_out_volt
    :field eps_controller_a_mpptx_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mpptx_temp
    :field eps_controller_a_mpptx_state: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mpptx_state
    :field eps_controller_a_mppty_pos_sol_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_pos_sol_volt
    :field eps_controller_a_mppty_pos_sol_curr: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_pos_sol_curr
    :field eps_controller_a_mppty_pos_out_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_pos_out_volt
    :field eps_controller_a_mppty_pos_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_pos_temp
    :field eps_controller_a_mppty_pos_state: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_pos_state
    :field eps_controller_a_mppty_neg_sol_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_neg_sol_volt
    :field eps_controller_a_mppty_neg_sol_curr: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_neg_sol_curr
    :field eps_controller_a_mppty_neg_out_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_neg_out_volt
    :field eps_controller_a_mppty_neg_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_neg_temp
    :field eps_controller_a_mppty_neg_state: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_mppty_neg_state
    :field eps_controller_a_distr_volt_3v3: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_volt_3v3
    :field eps_controller_a_distr_curr_3v3: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_curr_3v3
    :field eps_controller_a_distr_volt_5v: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_volt_5v
    :field eps_controller_a_distr_curr_5v: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_curr_5v
    :field eps_controller_a_distr_volt_vbat: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_volt_vbat
    :field eps_controller_a_distr_curr_vbat: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_curr_vbat
    :field eps_controller_a_distr_lcl_state: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_lcl_state
    :field eps_controller_a_distr_lcl_flagb: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_distr_lcl_flagb
    :field eps_controller_a_batc_volta: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_batc_volta
    :field eps_controller_a_batc_chrg_curr: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_batc_chrg_curr
    :field eps_controller_a_batc_dchrg_curr: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_batc_dchrg_curr
    :field eps_controller_a_batc_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_batc_temp
    :field eps_controller_a_batc_state: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_batc_state
    :field eps_controller_a_bp_temp_a: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_bp_temp_a
    :field eps_controller_a_bp_temp_b: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_bp_temp_b
    :field eps_controller_a_safety_ctr: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_safety_ctr
    :field eps_controller_a_pwr_cycles: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_pwr_cycles
    :field eps_controller_a_uptime: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_uptime
    :field eps_controller_a_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_temp
    :field eps_controller_a_supp_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_supp_temp
    :field eps_controller_b_3v3d_volt: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_b_3v3d_volt
    :field eps_controller_a_dcdc_3v3_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_dcdc_3v3_temp
    :field eps_controller_a_dcdc_5v_temp: ax25_frame.payload.ax25_info.payload.eps_controller_a.eps_controller_a_dcdc_5v_temp
    :field eps_controller_b_bptemp_c: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_bptemp_c
    :field eps_controller_b_battc_volt_b: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_battc_volt_b
    :field eps_controller_b_safety_ctr: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_safety_ctr
    :field eps_controller_b_pwr_cycles: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_pwr_cycles
    :field eps_controller_b_uptime: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_uptime
    :field eps_controller_b_temp: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_temp
    :field eps_controller_b_supp_temp: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_b_supp_temp
    :field eps_controller_a_3v3d_volt: ax25_frame.payload.ax25_info.payload.eps_controller_b.eps_controller_a_3v3d_volt
    :field imtq_mag_meas_1: ax25_frame.payload.ax25_info.payload.imtq.imtq_mag_meas_1
    :field imtq_mag_meas_2: ax25_frame.payload.ax25_info.payload.imtq.imtq_mag_meas_2
    :field imtq_mag_meas_3: ax25_frame.payload.ax25_info.payload.imtq.imtq_mag_meas_3
    :field imtq_coil_active_in_meas: ax25_frame.payload.ax25_info.payload.imtq_coil_active.imtq_coil_active_in_meas
    :field imtq_dipole_1: ax25_frame.payload.ax25_info.payload.imtq_dipole.imtq_dipole_1
    :field imtq_dipole_2: ax25_frame.payload.ax25_info.payload.imtq_dipole.imtq_dipole_2
    :field imtq_dipole_3: ax25_frame.payload.ax25_info.payload.imtq_dipole.imtq_dipole_3
    :field imtq_bdot_x: ax25_frame.payload.ax25_info.payload.imtq_bdot.imtq_bdot_x
    :field imtq_bdot_y: ax25_frame.payload.ax25_info.payload.imtq_bdot.imtq_bdot_y
    :field imtq_bdot_z: ax25_frame.payload.ax25_info.payload.imtq_bdot.imtq_bdot_z
    :field imtq_hskp_dig_volt: ax25_frame.payload.ax25_info.payload.imtq_hskp.imtq_hskp_dig_volt
    :field imtq_hskp_ana_volt: ax25_frame.payload.ax25_info.payload.imtq_hskp.imtq_hskp_ana_volt
    :field imtq_hskp_dig_curr: ax25_frame.payload.ax25_info.payload.imtq_hskp.imtq_hskp_dig_curr
    :field imtq_hskp_ana_curr: ax25_frame.payload.ax25_info.payload.imtq_hskp.imtq_hskp_ana_curr
    :field imtq_hskp_mcu_temp: ax25_frame.payload.ax25_info.payload.imtq_hskp.imtq_hskp_mcu_temp
    :field imtq_coil_current_x: ax25_frame.payload.ax25_info.payload.imtq_coil.imtq_coil_current_x
    :field imtq_coil_current_y: ax25_frame.payload.ax25_info.payload.imtq_coil.imtq_coil_current_y
    :field imtq_coil_current_z: ax25_frame.payload.ax25_info.payload.imtq_coil.imtq_coil_current_z
    :field imtq_temp_coil_x: ax25_frame.payload.ax25_info.payload.imtq_temp.imtq_temp_coil_x
    :field imtq_temp_coil_y: ax25_frame.payload.ax25_info.payload.imtq_temp.imtq_temp_coil_y
    :field imtq_temp_coil_z: ax25_frame.payload.ax25_info.payload.imtq_temp.imtq_temp_coil_z
    :field imtq_state_status: ax25_frame.payload.ax25_info.payload.imtq_state.imtq_state_status
    :field imtq_state_mode: ax25_frame.payload.ax25_info.payload.imtq_state.imtq_state_mode
    :field imtq_err_prev_iter: ax25_frame.payload.ax25_info.payload.imtq_state.imtq_err_prev_iter
    :field imtq_conf_changed: ax25_frame.payload.ax25_info.payload.imtq_state.imtq_conf_changed
    :field imtq_state_uptime: ax25_frame.payload.ax25_info.payload.imtq_state.imtq_state_uptime
    :field adcs_imtq_slftst_err_initial: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_initial
    :field adcs_imtq_slftst_err_pos_x: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_pos_x
    :field adcs_imtq_slftst_err_neg_x: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_neg_x
    :field adcs_imtq_slftst_err_pos_y: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_pos_y
    :field adcs_imtq_slftst_err_neg_y: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_neg_y
    :field adcs_imtq_slftst_err_pos_z: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_pos_z
    :field adcs_imtq_slftst_err_neg_z: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_neg_z
    :field adcs_imtq_slftst_err_final: ax25_frame.payload.ax25_info.payload.imtq_selftest.adcs_imtq_slftst_err_final
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = self._root.Ax25Frame(self._io, self, self._root)

    class Hdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.apid = self._io.read_u1()


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


    class Comm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.comm_tx_trsmtr_uptime = self._io.read_bits_int(17)
            self.comm_tx_bitrate = self._io.read_bits_int(2)
            self.comm_tx_last_tx_rf_refl_pwr = self._io.read_bits_int(12)
            self.comm_tx_last_tx_pamp_temp = self._io.read_bits_int(12)
            self.comm_tx_last_tx_last_tx_rf_fwd_pwr = self._io.read_bits_int(12)
            self.comm_tx_last_tx_curr_consmpt = self._io.read_bits_int(12)
            self.comm_tx_now_tx_fwd_pwr = self._io.read_bits_int(12)
            self.comm_tx_now_tx_curr_consmpt = self._io.read_bits_int(12)
            self.comm_tx_state_when_idle = self._io.read_bits_int(1) != 0
            self.comm_tx_beacon_state = self._io.read_bits_int(1) != 0
            self.comm_rx_uptime = self._io.read_bits_int(17)
            self.comm_rx_last_rx_doppler_offs = self._io.read_bits_int(12)
            self.comm_rx_last_rx_rssi = self._io.read_bits_int(12)
            self.comm_rx_now_doppler_offs = self._io.read_bits_int(12)
            self.comm_rx_now_rx_curr_consmpt = self._io.read_bits_int(12)
            self.comm_rx_supply_voltage = self._io.read_bits_int(12)
            self.comm_rx_osc_temp = self._io.read_bits_int(12)
            self.comm_rx_now_pamp_temp = self._io.read_bits_int(12)
            self.comm_rx_now_rssi = self._io.read_bits_int(12)


    class ImtqHskp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_hskp_dig_volt = self._io.read_u2le()
            self.imtq_hskp_ana_volt = self._io.read_u2le()
            self.imtq_hskp_dig_curr = self._io.read_u2le()
            self.imtq_hskp_ana_curr = self._io.read_u2le()
            self.imtq_hskp_mcu_temp = self._io.read_u2le()


    class Experiments(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.experiments_curr_exp_code = self._io.read_bits_int(4)
            self._io.align_to_byte()
            self.experiments_exp_startup_res = self._io.read_u1()
            self.experiments_last_exp_iter_stat_status = self._io.read_u1()


    class PeriodicMsg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.periodic_msg_data = (self._io.read_bytes((self._io.size() - 1))).decode(u"ASCII")


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


    class EpsControllerB(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_controller_b_bptemp_c = self._io.read_bits_int(10)
            self.eps_controller_b_battc_volt_b = self._io.read_bits_int(10)
            self._io.align_to_byte()
            self.eps_controller_b_safety_ctr = self._io.read_u1()
            self.eps_controller_b_pwr_cycles = self._io.read_u2le()
            self.eps_controller_b_uptime = self._io.read_u4le()
            self.eps_controller_b_temp = self._io.read_bits_int(10)
            self.eps_controller_b_supp_temp = self._io.read_bits_int(10)
            self.eps_controller_a_3v3d_volt = self._io.read_bits_int(10)


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self.pid
            if _on == 240:
                self._raw_ax25_info = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = self._root.Frame(io, self, self._root)
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


    class ImtqDipole(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_dipole_1 = self._io.read_u2le()
            self.imtq_dipole_2 = self._io.read_u2le()
            self.imtq_dipole_3 = self._io.read_u2le()


    class ImtqSelftest(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adcs_imtq_slftst_err_initial = self._io.read_u1()
            self.adcs_imtq_slftst_err_pos_x = self._io.read_u1()
            self.adcs_imtq_slftst_err_neg_x = self._io.read_u1()
            self.adcs_imtq_slftst_err_pos_y = self._io.read_u1()
            self.adcs_imtq_slftst_err_neg_y = self._io.read_u1()
            self.adcs_imtq_slftst_err_pos_z = self._io.read_u1()
            self.adcs_imtq_slftst_err_neg_z = self._io.read_u1()
            self.adcs_imtq_slftst_err_final = self._io.read_u1()


    class ImtqBdot(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_bdot_x = self._io.read_u4le()
            self.imtq_bdot_y = self._io.read_u4le()
            self.imtq_bdot_z = self._io.read_u4le()


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hdr = self._root.Hdr(self._io, self, self._root)
            _on = (self.hdr.apid & 63)
            if _on == 5:
                self.payload = self._root.PeriodicMsg(self._io, self, self._root)
            elif _on == 13:
                self.payload = self._root.Telemetry(self._io, self, self._root)


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


    class ImtqCoilActive(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_coil_active_in_meas = self._io.read_bits_int(1) != 0


    class ImtqState(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_state_status = self._io.read_u1()
            self.imtq_state_mode = self._io.read_bits_int(2)
            self._io.align_to_byte()
            self.imtq_err_prev_iter = self._io.read_u1()
            self.imtq_conf_changed = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.imtq_state_uptime = self._io.read_u4le()


    class ImtqTemp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_temp_coil_x = self._io.read_u2le()
            self.imtq_temp_coil_y = self._io.read_u2le()
            self.imtq_temp_coil_z = self._io.read_u2le()


    class HardwareState(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hardware_state_gpio_sail_deployed = self._io.read_bits_int(1) != 0
            self.hardware_state_mcu_temp = self._io.read_bits_int(12)


    class Antennas(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.antennas_ant1_depl_sw_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant2_depl_sw_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant3_depl_sw_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant4_depl_sw_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant1_depl_sw_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant2_depl_sw_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant3_depl_sw_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant4_depl_sw_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant1_last_timed_stop_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant2_last_timed_stop_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant3_last_timed_stop_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant4_last_timed_stop_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant1_last_timed_stop_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant2_last_timed_stop_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant3_last_timed_stop_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant4_last_timed_stop_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant1_burn_active_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant2_burn_active_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant3_burn_active_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant4_burn_active_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant1_burn_active_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant2_burn_active_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant3_burn_active_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant4_burn_active_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_sys_indep_burn_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_sys_indep_burn_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant_ignoring_sw_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_ant_ignoring_sw_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_armed_ch_a = self._io.read_bits_int(1) != 0
            self.antennas_armed_ch_b = self._io.read_bits_int(1) != 0
            self.antennas_ant1_activation_cnt_ch_a = self._io.read_bits_int(3)
            self.antennas_ant2_activation_cnt_ch_a = self._io.read_bits_int(3)
            self.antennas_ant3_activation_cnt_ch_a = self._io.read_bits_int(3)
            self.antennas_ant4_activation_cnt_ch_a = self._io.read_bits_int(3)
            self.antennas_ant1_activation_cnt_ch_b = self._io.read_bits_int(3)
            self.antennas_ant2_activation_cnt_ch_b = self._io.read_bits_int(3)
            self.antennas_ant3_activation_cnt_ch_b = self._io.read_bits_int(3)
            self.antennas_ant4_activation_cnt_ch_b = self._io.read_bits_int(3)
            self.antennas_ant1_activation_time_ch_a = self._io.read_bits_int(3)
            self.antennas_ant2_activation_time_ch_a = self._io.read_bits_int(3)
            self.antennas_ant3_activation_time_ch_a = self._io.read_bits_int(3)
            self.antennas_ant4_activation_time_ch_a = self._io.read_bits_int(3)
            self.antennas_ant1_activation_time_ch_b = self._io.read_bits_int(3)
            self.antennas_ant2_activation_time_ch_b = self._io.read_bits_int(3)
            self.antennas_ant3_activation_time_ch_b = self._io.read_bits_int(3)
            self.antennas_ant4_activation_time_ch_b = self._io.read_bits_int(3)


    class Imtq(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_mag_meas_1 = self._io.read_u4le()
            self.imtq_mag_meas_2 = self._io.read_u4le()
            self.imtq_mag_meas_3 = self._io.read_u4le()


    class Obc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.obc_boot_ctr = self._io.read_u4le()
            self.obc_boot_idx = self._io.read_u1()
            self.obc_reboot_reason = self._io.read_u2le()
            self.obc_code_crc = self._io.read_u2le()
            self.obc_mission_time = self._io.read_u8le()
            self.obc_ext_time = self._io.read_u4le()
            self.obc_comm_err = self._io.read_u1()
            self.obc_eps_err = self._io.read_u1()
            self.obc_rtc_err = self._io.read_u1()
            self.obc_imtq_err = self._io.read_u1()
            self.obc_n25qflash1_err = self._io.read_u1()
            self.obc_n25qflash2_err = self._io.read_u1()
            self.obc_n25qflash3_err = self._io.read_u1()
            self.obc_n25q_tmr_corr = self._io.read_u1()
            self.obc_fram_tmr_corr = self._io.read_u1()
            self.obc_payload_err = self._io.read_u1()
            self.obc_cam_err = self._io.read_u1()
            self.obc_suns_exp_err = self._io.read_u1()
            self.obc_ant_prim_err = self._io.read_u1()
            self.obc_ant_sec_err = self._io.read_u1()
            self.obc_prim_flash_scrbg_ptr = self._io.read_bits_int(3)
            self.obc_sec_flash_scrbg_ptr = self._io.read_bits_int(3)
            self._io.align_to_byte()
            self.obc_ram_scrbg_ptr = self._io.read_u4le()
            self.obc_system_uptime = self._io.read_bits_int(22)
            self._io.align_to_byte()
            self.obc_system_flash_free = self._io.read_u4le()


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


    class EpsControllerA(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_controller_a_mpptx_sol_volt = self._io.read_bits_int(12)
            self.eps_controller_a_mpptx_sol_curr = self._io.read_bits_int(12)
            self.eps_controller_a_mpptx_out_volt = self._io.read_bits_int(12)
            self.eps_controller_a_mpptx_temp = self._io.read_bits_int(12)
            self.eps_controller_a_mpptx_state = self._io.read_bits_int(3)
            self.eps_controller_a_mppty_pos_sol_volt = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_pos_sol_curr = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_pos_out_volt = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_pos_temp = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_pos_state = self._io.read_bits_int(3)
            self.eps_controller_a_mppty_neg_sol_volt = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_neg_sol_curr = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_neg_out_volt = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_neg_temp = self._io.read_bits_int(12)
            self.eps_controller_a_mppty_neg_state = self._io.read_bits_int(3)
            self.eps_controller_a_distr_volt_3v3 = self._io.read_bits_int(10)
            self.eps_controller_a_distr_curr_3v3 = self._io.read_bits_int(10)
            self.eps_controller_a_distr_volt_5v = self._io.read_bits_int(10)
            self.eps_controller_a_distr_curr_5v = self._io.read_bits_int(10)
            self.eps_controller_a_distr_volt_vbat = self._io.read_bits_int(10)
            self.eps_controller_a_distr_curr_vbat = self._io.read_bits_int(10)
            self.eps_controller_a_distr_lcl_state = self._io.read_bits_int(7)
            self.eps_controller_a_distr_lcl_flagb = self._io.read_bits_int(6)
            self.eps_controller_a_batc_volta = self._io.read_bits_int(10)
            self.eps_controller_a_batc_chrg_curr = self._io.read_bits_int(10)
            self.eps_controller_a_batc_dchrg_curr = self._io.read_bits_int(10)
            self.eps_controller_a_batc_temp = self._io.read_bits_int(10)
            self.eps_controller_a_batc_state = self._io.read_bits_int(3)
            self.eps_controller_a_bp_temp_a = self._io.read_bits_int(13)
            self.eps_controller_a_bp_temp_b = self._io.read_bits_int(13)
            self._io.align_to_byte()
            self.eps_controller_a_safety_ctr = self._io.read_u1()
            self.eps_controller_a_pwr_cycles = self._io.read_u2le()
            self.eps_controller_a_uptime = self._io.read_u4le()
            self.eps_controller_a_temp = self._io.read_bits_int(10)
            self.eps_controller_a_supp_temp = self._io.read_bits_int(10)
            self.eps_controller_b_3v3d_volt = self._io.read_bits_int(10)
            self.eps_controller_a_dcdc_3v3_temp = self._io.read_bits_int(10)
            self.eps_controller_a_dcdc_5v_temp = self._io.read_bits_int(10)


    class Gyroscope(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gyroscope_x_meas = self._io.read_u2le()
            self.gyroscope_y_meas = self._io.read_u2le()
            self.gyroscope_z_meas = self._io.read_u2le()
            self.gyroscope_temp = self._io.read_u2le()


    class ImtqCoil(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imtq_coil_current_x = self._io.read_u2le()
            self.imtq_coil_current_y = self._io.read_u2le()
            self.imtq_coil_current_z = self._io.read_u2le()


    class Telemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.obc = self._root.Obc(self._io, self, self._root)
            self.antennas = self._root.Antennas(self._io, self, self._root)
            self.experiments = self._root.Experiments(self._io, self, self._root)
            self.gyroscope = self._root.Gyroscope(self._io, self, self._root)
            self.comm = self._root.Comm(self._io, self, self._root)
            self.hardware_state = self._root.HardwareState(self._io, self, self._root)
            self.eps_controller_a = self._root.EpsControllerA(self._io, self, self._root)
            self.eps_controller_b = self._root.EpsControllerB(self._io, self, self._root)
            self.imtq = self._root.Imtq(self._io, self, self._root)
            self.imtq_coil_active = self._root.ImtqCoilActive(self._io, self, self._root)
            self.imtq_dipole = self._root.ImtqDipole(self._io, self, self._root)
            self.imtq_bdot = self._root.ImtqBdot(self._io, self, self._root)
            self.imtq_hskp = self._root.ImtqHskp(self._io, self, self._root)
            self.imtq_coil = self._root.ImtqCoil(self._io, self, self._root)
            self.imtq_temp = self._root.ImtqTemp(self._io, self, self._root)
            self.imtq_state = self._root.ImtqState(self._io, self, self._root)
            self.imtq_selftest = self._root.ImtqSelftest(self._io, self, self._root)



