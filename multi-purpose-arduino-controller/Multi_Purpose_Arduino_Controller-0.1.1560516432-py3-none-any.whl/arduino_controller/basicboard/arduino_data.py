from ..arduino_variable import arduio_variable

FIRSTFREEEEPROM = 8+2 #id + idcs

def definitions(self):
    from ..portrequest import DATABYTEPOSITION

    return {
        "STARTANALOG": 0,
        "ENDANALOG": 100,
        "STARTBYTE": 2,
        "STARTBYTEPOSITION": 0,
        "COMMANDBYTEPOSITION": 1,
        "LENBYTEPOSITION": 2,
        "DATABYTEPOSITION": 3,
        "MAXFUNCTIONS": str(len(self.portcommands)),
        "SERIALARRAYSIZE": str(
            DATABYTEPOSITION
            + max(
                *[
                    max(portcommand.receivelength, portcommand.sendlength)
                    for portcommand in self.portcommands
                ]
            )
            + 2
        ),
        "BAUD": 9600,
     #   "DATARATE": 200,
    }


def global_vars(self):
    print({ard_var.name: [ard_var.type, ard_var.value] for attr,ard_var in self.get_arduino_vars().items()},)
    return {
        **{name: ["uint8_t", str(pin.position)] for name, pin in self.pins.items()},
        **{ard_var.name: [ard_var.type, ard_var.value] for attr,ard_var in self.get_arduino_vars().items()},
        "writedata[SERIALARRAYSIZE]": ["uint8_t", None],
        "serialread[SERIALARRAYSIZE]": ["uint8_t", None],
        "serialreadpos": ["uint8_t", 0],
        "commandlength": ["uint8_t", 0],
        "cmds[MAXFUNCTIONS ]": ["uint8_t", None],
        "cmd_length[MAXFUNCTIONS]": ["uint8_t", None],
        "(*cmd_calls[MAXFUNCTIONS])(uint8_t* data, uint8_t s)": ["void", None],
        "lastdata": ["uint32_t", 0],
        "ct": ["uint32_t", None],
   #     "datarate": ["uint32_t", "DATARATE"],
        "c": ["uint8_t", None],
        "identified": ["bool", "false"],
    }


def includes(self):
    return ["<EEPROM.h>"]


def functions(self):
    return {
        "generate_checksum": [
            "uint16_t",
            [("uint8_t*", "data"), ("int", "count")],
            "uint16_t sum1 = 0;\n"
            "uint16_t sum2 = 0;\n"
            "for (int index = 0; index < count; ++index ) {\n"
            "sum1 = (sum1 + data[index]) % 255;\n"
            "sum2 = (sum2 + sum1) % 255;\n"
            "}\n"
            "return (sum2 << 8) | sum1;\n",
        ],
        "write_data_array": [
            "void",
            [("uint8_t*", "data"), ("uint8_t", "cmd"), ("uint8_t", "len")],
            "writedata[STARTBYTEPOSITION] = STARTBYTE;\n"
            "writedata[COMMANDBYTEPOSITION] = cmd;\n"
            "writedata[LENBYTEPOSITION] = len;\n"
            "for (uint8_t i = 0; i < len; i++) {\n"
            "writedata[DATABYTEPOSITION + i] = data[i];\n"
            "}"
            "uint16_t cs = generate_checksum(writedata, len + DATABYTEPOSITION);\n"
            "writedata[DATABYTEPOSITION + len] = cs >> 8;\n"
            "writedata[DATABYTEPOSITION + len + 1] = cs >> 0;\n"
            "Serial.write(writedata, len + DATABYTEPOSITION + 2);\n",
        ],
        "write_data": [
            "template< typename T> void",
            [("T", "data"), ("uint8_t", "cmd")],
            "uint8_t d[sizeof(T)];\n"
            "for (uint8_t i = 0;i<sizeof(T) ; i++) {\n"
            "d[i] = (uint8_t) (data >> (8 * i) & 0xff );\n"
            "}\n"
            "write_data_array(d, cmd, sizeof(T));\n",
        ],
        "get_id": [
            "uint64_t",
            [],
            "uint64_t id;\n" "EEPROM.get(0, id);\n" "return id;\n",
        ],
        "checkUUID": [
            "void",
            [],
            "uint64_t id = get_id();\n"
            "uint16_t cs = generate_checksum((uint8_t*)&id, sizeof(id));\n"
            "uint16_t cs2;\n"
            "EEPROM.get(sizeof(id), cs2);\n"
            "if (cs != cs2) {\n"
            "id = (uint64_t)("
            "(((uint64_t)random()) << 48) | "
            "(((uint64_t)random()) << 32) | "
            "(((uint64_t)random()) << 16) | "
            "(((uint64_t)random()))"
            ");\n"
            "EEPROM.put(0, id);\n"
            "EEPROM.put(sizeof(id), generate_checksum((uint8_t*)&id, sizeof(id)));\n"
            "}\n",
        ],
        "add_command": [
            "void",
            [
                ("uint8_t", "cmd"),
                ("uint8_t", "len"),
                ("void", "(*func)(uint8_t* data, uint8_t s)"),
            ],
            "for (uint8_t i = 0; i < MAXFUNCTIONS; i++ ) {\n"
            "if (cmds[i] == 255) {\n"
            "cmds[i] = cmd;\n"
            "cmd_length[i] = len;\n"
            "cmd_calls[i] = func;\n"
            "return;\n"
            "}\n"
            "}\n",
        ],
        "endread": [
            "void",
            [],
            "commandlength = 0;\n" "serialreadpos = STARTBYTEPOSITION;\n",
        ],
        "get_cmd_index": [
            "uint8_t",
            [("uint8_t", "cmd")],
            "for (uint8_t i = 0; i < MAXFUNCTIONS; i++ ) {\n"
            "if (cmds[i] == cmd) {\n"
            "return i;\n"
            "}\n"
            "}\n"
            ""
            "return 255;",
        ],
        "validate_serial_command": [
            "void",
            [],
            "if(generate_checksum(serialread, DATABYTEPOSITION + serialread[LENBYTEPOSITION]) == (uint16_t)(serialread[DATABYTEPOSITION + serialread[LENBYTEPOSITION]] << 8) + serialread[DATABYTEPOSITION + serialread[LENBYTEPOSITION]+1]){\n"
            "uint8_t cmd_index = get_cmd_index(serialread[COMMANDBYTEPOSITION]);\n"
            "if(cmd_index != 255){\n"
            "uint8_t data[serialread[LENBYTEPOSITION]];\n"
            "memcpy(data,&serialread[DATABYTEPOSITION],serialread[LENBYTEPOSITION]);\n"
            "cmd_calls[cmd_index](data,serialread[LENBYTEPOSITION]);\n"
            "}\n"
            "}\n",
        ],
        "readloop": [
            "uint64_t",
            [],
            "while(Serial.available() > 0) {\n"
            "c = Serial.read();\n"
            "serialread[serialreadpos] = c;\n"
            "if (serialreadpos == STARTBYTEPOSITION) {\n"
            "if (c == STARTBYTE) {\n"
            "} else {\n"
            "endread();\n"
            "continue;\n"
            "}\n"
            "}\n"
            "else {\n"
            "if (serialreadpos == LENBYTEPOSITION) {\n"
            "commandlength = c;\n"
            "} else if (serialreadpos - commandlength > DATABYTEPOSITION + 1 ) { //stx cmd len cs cs (len = 0; pos = 4)\n"
            "endread();\n"
            "continue;\n"
            "}\n"
            "else if (serialreadpos - commandlength == DATABYTEPOSITION + 1) {\n"
            "validate_serial_command();\n"
            "endread();\n"
            "continue;\n"
            "}\n"
            "}\n"
            "serialreadpos++;\n"
            "}\n",
        ],
        **{
            portcommand.name
            + "_"
            + str(portcommand.byteid): [
                "void",
                [("uint8_t*", "data"), ("uint8_t", "s")],
                portcommand.arduino_code,
            ]
            for portcommand in self.portcommands
        },
    }


def setup(self):
    setup = (
        "Serial.begin(BAUD);\n"
        "while (!Serial) {;}\n"
        "for (int i = STARTANALOG; i < ENDANALOG; i++) {\n"
        "randomSeed(analogRead(i)*random());\n"
        "}\n"
        "checkUUID();\n"
        "for (uint8_t i = 0; i < MAXFUNCTIONS; i++ ) {\n"
        "cmds[i] = 255;\n"
        "}\n"
        "ct = millis();\n"
    )
    for name, pin in self.pins.items():
        setup += "pinMode(" + name + ", " + pin.arduinoMode() + ");\n"
    for portcommand in self.portcommands:
        setup += (
            "add_command("
            + str(portcommand.byteid)
            + ", "
            + str(portcommand.sendlength)
            + ", "
            + portcommand.name
            + "_"
            + str(portcommand.byteid)
            + ");\n"
        )
    return setup


def loop(self):
    return (
        "readloop();\n"
        "ct = millis();\n"
        "if(ct-lastdata>datarate && identified){\n"
        "dataloop();\n"
        "lastdata=ct;\n"
        "}\n"
    )


def dataloop(self):
    return ""


def create(self):
    return {
        "definitions": definitions(self),
        "global_vars": global_vars(self),
        "includes": includes(self),
        "functions": functions(self),
        "setup": setup(self),
        "loop": loop(self),
        "dataloop": dataloop(self),
    }
