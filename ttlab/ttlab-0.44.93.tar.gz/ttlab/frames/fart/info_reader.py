import re


class InfoReader:

    @staticmethod
    def read_info_from_file(filename):
        info_text = InfoReader._read_header_from_file(filename)
        info = {
            'x pixels': InfoReader._read_x_pixels(info_text),
            'y pixels': InfoReader._read_y_pixels(info_text),
            'exposure time': InfoReader._read_exposure_time(info_text),
            'number of accumulations': InfoReader._read_number_of_accumulations(info_text),
            'vertical binning': InfoReader._read_vertical_binning(info_text),
            'horisontal binning': InfoReader._read_horisontal_binning(info_text),
            'pixel readout rate': InfoReader._read_pixel_readout_rate(info_text),
            'overlap readout': InfoReader._read_overlap_readout(info_text),
            'spurious noise filter': InfoReader._read_spurious_noise_filter(info_text),
            'cycle mode': InfoReader._read_cycle_mode(info_text),
            'trigger mode': InfoReader._read_trigger_mode(info_text),
            'simple pre amp gain control': InfoReader._read_simple_pre_amp_gain_control(info_text),
            'pixel encoding': InfoReader._read_pixel_encoding(info_text),
            'fan speed': InfoReader._read_fan_speed(info_text),
            'electronic shuttering mode': InfoReader._read_electronic_shuttering_mode(info_text),
            'fast AOI frame rate enabled': InfoReader._read_fast_AOI_frame_rate_enabled(info_text)
        }
        return info

    @staticmethod
    def read_info_from_gridfs(gridfs):
        info_text = InfoReader._read_header_from_gridfs(gridfs)
        info = {
            'x pixels': InfoReader._read_x_pixels(info_text),
            'y pixels': InfoReader._read_y_pixels(info_text),
            'exposure time': InfoReader._read_exposure_time(info_text),
            'number of accumulations': InfoReader._read_number_of_accumulations(info_text),
            'vertical binning': InfoReader._read_vertical_binning(info_text),
            'horisontal binning': InfoReader._read_horisontal_binning(info_text),
            'pixel readout rate': InfoReader._read_pixel_readout_rate(info_text),
            'overlap readout': InfoReader._read_overlap_readout(info_text),
            'spurious noise filter': InfoReader._read_spurious_noise_filter(info_text),
            'cycle mode': InfoReader._read_cycle_mode(info_text),
            'trigger mode': InfoReader._read_trigger_mode(info_text),
            'simple pre amp gain control': InfoReader._read_simple_pre_amp_gain_control(info_text),
            'pixel encoding': InfoReader._read_pixel_encoding(info_text),
            'fan speed': InfoReader._read_fan_speed(info_text),
            'electronic shuttering mode': InfoReader._read_electronic_shuttering_mode(info_text),
            'fast AOI frame rate enabled': InfoReader._read_fast_AOI_frame_rate_enabled(info_text)
        }
        return info

    @staticmethod
    def _read_header_from_gridfs(gridfs):
        line = gridfs.readline()
        line_nr = 0
        header_text = ''
        while line is not b'':
            decoded_line = line.decode("utf-8")
            header_text += decoded_line
            if 'Time, Intensity:' in decoded_line or line_nr > 100:
                return header_text
            line = gridfs.readline()
            line_nr += 1

    @staticmethod
    def _read_header_from_file(filename):
        info_text = ''
        with open(filename) as file:
            for line_nr, line in enumerate(file):
                info_text += line
                if 'Time, Intensity:' in line or line_nr > 100:
                    return info_text


    @staticmethod
    def _read_x_pixels(info_text):
        return int(re.search("(?<=imageWidth:\t)\\d*(?=\n)", info_text).group())

    @staticmethod
    def _read_y_pixels(info_text):
        return int(re.search("(?<=imageHeight:\t)\\d*(?=\n)", info_text).group())

    @staticmethod
    def _read_exposure_time(info_text):
        return float(re.search("(?<=exposureTime:\t)\\d.\\d*(?=\n)", info_text).group())

    @staticmethod
    def _read_number_of_accumulations(info_text):
        return int(re.search("(?<=numberOfAccumulations:\t)\\d*(?=\n)", info_text).group())

    @staticmethod
    def _read_vertical_binning(info_text):
        return int(re.search("(?<=verticalBinning:\t)\\d*(?=\n)", info_text).group())

    @staticmethod
    def _read_horisontal_binning(info_text):
        return int(re.search("(?<=horisontalBinning:\t)\\d*(?=\n)", info_text).group())

    @staticmethod
    def _read_pixel_readout_rate(info_text):
        return re.search("(?<=pixelReadoutRate:\t)\\d+\\s\\w+(?=\n)", info_text).group()

    @staticmethod
    def _read_overlap_readout(info_text):
        return re.search("(?<=overlapReadout:\t)\\d(?=\n)", info_text).group() == '1'

    @staticmethod
    def _read_spurious_noise_filter(info_text):
        return re.search("(?<=spuriousNoiseFilter:\t)\\d(?=\n)", info_text).group() == '1'

    @staticmethod
    def _read_cycle_mode(info_text):
        return re.search("(?<=cycleMode:\t)\\w+(?=\n)", info_text).group()

    @staticmethod
    def _read_trigger_mode(info_text):
        return re.search("(?<=triggerMode:\t)\\w+(?=\n)", info_text).group()

    @staticmethod
    def _read_simple_pre_amp_gain_control(info_text):
        return re.search("(?<=simplePreAmpGainControl:\t).+(?=\n)", info_text).group()

    @staticmethod
    def _read_pixel_encoding(info_text):
        return re.search("(?<=pixelEncoding:\t)\\w+\\d+(?=\n)", info_text).group()

    @staticmethod
    def _read_fan_speed(info_text):
        return re.search("(?<=fanSpeed:\t)\\w+(?=\n)", info_text).group()

    @staticmethod
    def _read_electronic_shuttering_mode(info_text):
        return re.search("(?<=electronicShutteringMode:\t)\\w+(?=\n)", info_text).group()

    @staticmethod
    def _read_fast_AOI_frame_rate_enabled(info_text):
        return re.search("(?<=fastAOIFrameRateEnable:\t)\\w+(?=\n)", info_text).group() == '1'
