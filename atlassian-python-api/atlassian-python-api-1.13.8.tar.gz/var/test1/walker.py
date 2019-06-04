#!/usr/bin/env python
import os

JAVA_CLASS_EXTENSION = ".class"
BLOCK_SIZE = 8
EXCLUDE_JAVA_VERSION = "Java SE 8"


def read_block_size_check_java_version(filename, block_size):
    with open(filename, "rb") as file_name:
        block = file_name.read(block_size)
        output = ""
        if not (ord(block[0]) == 0xCA and
                ord(block[1]) == 0xFE and
                ord(block[2]) == 0xBA and
                ord(block[3]) == 0xBE):
            return ""

        major_version_byte = ord(block[7])
        if major_version_byte == 0x39:
            output = "Java SE 13"
        elif major_version_byte == 0x38:
            output = "Java SE 12"
        elif major_version_byte == 0x37:
            output = "Java SE 11"
        elif major_version_byte == 0x36:
            output = "Java SE 10"
        elif major_version_byte == 0x35:
            output = "Java SE 9"
        elif major_version_byte == 0x34:
            output = "Java SE 8"
        elif major_version_byte == 0x33:
            output = "Java SE 7"
        elif major_version_byte == 0x32:
            output = "Java SE 6.0"
        elif major_version_byte == 0x31:
            output = "Java SE 5.0"
        elif major_version_byte == 0x30:
            output = "JDK 1.4"
        elif major_version_byte == 0x2F:
            output = "JDK 1.3"
        elif major_version_byte == 0x2E:
            output = "JDK 1.2"
        elif major_version_byte == 0x2D:
            output = "JDK 1.1"
        return output


def run_walker():
    for r, s, f in os.walk("."):
        for i in f:
            if i.endswith(JAVA_CLASS_EXTENSION):
                path_to_file = os.path.join(r, i)
                built_java_version = read_block_size_check_java_version(path_to_file, BLOCK_SIZE)
                if len(built_java_version) > 0 and built_java_version != EXCLUDE_JAVA_VERSION:
                    print(built_java_version + '\t' + path_to_file)


if __name__ == '__main__':
    run_walker()
