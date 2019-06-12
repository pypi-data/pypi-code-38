# ©2018 - Tim van Leuverden <TvanLeuverden@Gmail.com>
import os
import re
import zlib
from progressbar import ProgressBar


class Crc32(object):
    def __init__(self, assistant):
        self.assistant = assistant

    def crc32(self, file):
        crc_calculated = None
        crc_found = None

        # Find any CRC in filename
        try:
            crc_calculated = self.crc32_checksum(file)
            self.assistant.logger.debug("crc_calculated: %s" % str(crc_calculated))
            crc_found = re.split("([a-fA-F0-9]{8})", file)[-2]
            self.assistant.logger.debug("crc_found: %s" % str(crc_found))
        # No CRC in filename found
        except (IndexError, ValueError) as e:
            self.assistant.logger.debug("Error: %s" % str(e))
            self.assistant.not_found += 1
            if not self.assistant.quiet_mode:
                self.assistant.logger.warning(
                    "%s%s\t%s" % (
                        self.assistant.CLEAN_LINE,
                        self.assistant.text_yellow("⁉  " + crc_calculated), # ⚠
                        self.assistant.text_default(file)
                    )
                )
            else:
                print(
                    "%s  %s" % (
                        crc_calculated,
                        file
                    )
                )
        # Actual error
        except (IOError, OSError) as e:
            self.assistant.logger.debug("Error: %s" % str(e))
            self.assistant.failed += 1
            if not self.assistant.quiet_mode:
                self.assistant.logger.error(
                    "%s\t%s\t%s\t%s" % (
                        self.assistant.text_purple("‼  ERROR"),
                        self.assistant.text_default(e.strerror or e.errno),
                        self.assistant.text_purple("AT"),
                        self.assistant.text_default(file)
                    )
                )
        # CRC found in filename
        else:
            if crc_calculated == crc_found.upper():
                # CRCs don't match
                crc_found_color = self.assistant.text_green(crc_found)
                crc_calculated_color = self.assistant.text_green("✔  ️" + crc_found)
                self.assistant.successful += 1
            else:
                # CRCs don't match
                crc_found_color = self.assistant.text_red(crc_found)
                crc_calculated_color = self.assistant.text_red("✖  " + crc_calculated)
                self.assistant.no_match += 1

            filename_split = file.split(crc_found)

            # Print result
            if not self.assistant.quiet_mode:
                self.assistant.logger.info(
                    "%s%s\t%s%s%s" % (
                        self.assistant.CLEAN_LINE,
                        crc_calculated_color,
                        self.assistant.text_default(filename_split[0]),
                        crc_found_color,
                        self.assistant.text_default(filename_split[1])
                    )
                )
            else:
                print(
                    "%s  %s" % (
                        crc_calculated,
                        file
                    )
                )

        return file

    def crc32_checksum(self, filename):
        self.assistant.logger.debug("filename: %s" % filename)
        crc = 0
        file = open(filename, "rb")
        buff_size = 65536
        done = 0
        size = os.path.getsize(filename)
        self.assistant.logger.debug("size: %s" % str(size))
        if not self.assistant.quiet_mode:
            progress_bar = ProgressBar(widgets=self.assistant.WIDGETS, max_value=size)
            progress_bar.start()
        try:
            while True:
                data = file.read(buff_size)
                done += buff_size
                if not data:
                    if not self.assistant.quiet_mode:
                        progress_bar.finish()
                    self.assistant.logger.debug("data: %s" % str(data))
                    break
                else:
                    if not self.assistant.quiet_mode:
                        try:
                            progress_bar.update(done)
                        except:
                            pass
                crc = zlib.crc32(data, crc)
        except KeyboardInterrupt:
            if not self.assistant.quiet_mode:
                progress_bar.finish()
            self.assistant.logger.debug("crc32_checksum: KeyboardInterrupt")
            file.close()
            return None
        self.assistant.logger.debug("done: %s" % str(done))
        file.close()
        if crc < 0:
            crc &= 2 ** 32 - 1
        return "%.8X" % crc
