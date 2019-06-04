class SystemInfoManager:
    def __init__(self):
        return

    def get_system_info(self):
        """
        Gets the current system data
        (e.g. uptime, free memory, cpu usage etc.)
        :return:
        """
        systeminfo = []

        # Remote-ID
        #systeminfo.append({'name': 'Remote-ID', 'type': 'remote', 'value': db.get_server_data("REMOTE_ID", Database())})

        #Laufzeit
        uptime = "xy Stunden"
        systeminfo.append({'name': 'Laufzeit', 'type': 'uptime', 'value': uptime})

        #CPU-Temperatur
        cpu_temp = 35
        systeminfo.append({'name': 'CPU-Temp', 'type': 'cputemp', 'value': str(cpu_temp)+" &deg;"})

        #Kernel-Version
        kernel = "Version x.y"
        systeminfo.append({'name': 'Kernel', 'type': 'kernel', 'value': kernel})

        #Speichernutzung
        space_usage = "25%"
        systeminfo.append({'name': 'Speichernutzung', 'type': 'spaceusage', 'value': space_usage})

        #Freier Speicher
        free_space = "120Gb"
        systeminfo.append({'name': 'Freier Speicher', 'type': 'freespace', 'value': free_space})

        #RAM-Auslastung
        ram_usage = "37%"
        systeminfo.append({'name': 'RAM-Nutzung', 'type': 'ramusage', 'value': ram_usage})

        #Firmware
        firmware = "Firmware x.y.z"
        systeminfo.append({'name': 'Firmware', 'type': 'firmware', 'value': firmware})

        #Remote-ID
        systeminfo.append({'name': 'Firmware', 'type': 'firmware', 'value': firmware})

        return {'systeminfo': systeminfo}