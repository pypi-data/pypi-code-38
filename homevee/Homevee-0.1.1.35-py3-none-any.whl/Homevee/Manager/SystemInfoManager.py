import datetime

import psutil

from Homevee.Utils import Constants


class SystemInfoManager:
    def __init__(self):
        return

    def get_avg_cpu_temp(self):
        temps = psutil.sensors_temperatures(fahrenheit=False)['coretemp']
        temp_sum = 0
        for temp in temps:
            temp_sum += temp.current
        return temp_sum/len(temps)

    def get_free_space_data(self):
        free_space = psutil.disk_usage(Constants.HOMEVEE_DIR).free
        division_counter = 0
        label_division_map = {
            0: "Byte",
            1: "kB",
            2: "MB",
            3: "GB",
            4: "TB"
        }

        free_space_label = "Byte"

        while True:
            if division_counter+1 not in label_division_map or free_space < 1024:
                break

            free_space = free_space/1024
            division_counter += 1
            free_space_label = label_division_map[division_counter]

        return round(free_space, 2), free_space_label

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
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = boot_time.strftime("%H:%M %d.%m.%Y")
        systeminfo.append({'name': 'Aktiv seit', 'type': 'uptime', 'value': uptime})

        try:
            #CPU-Temperatur
            cpu_temp = self.get_avg_cpu_temp()
            systeminfo.append({'name': 'CPU-Temp', 'type': 'cputemp', 'value': str(cpu_temp)+" &deg;"})
        except:
            #only compatible with linux for now
            pass

        #CPU-Auslastung
        cpu_usage = psutil.cpu_percent(interval=None)
        systeminfo.append({'name': 'CPU-Auslastung', 'type': 'cpuusage', 'value': str(cpu_usage)+" %"})

        #CPU-Kerne
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count()
        systeminfo.append({'name': 'CPU-Kerne', 'type': 'cpucores', 'value': str(cpu_cores)+" Kerne\n("+str(cpu_threads)+" Threads)"})

        #CPU-Takt
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = round(cpu_freq/1000, 2)
        systeminfo.append({'name': 'CPU-Takt', 'type': 'cpufrequency', 'value': str(cpu_freq)+" GHz"})

        #Kernel-Version
        systeminfo.append({'name': 'Version', 'type': 'version', 'value': Constants.HOMEVEE_VERSION_NUMBER})

        #Speichernutzung
        space_usage = psutil.disk_usage(Constants.HOMEVEE_DIR).percent
        systeminfo.append({'name': 'Speichernutzung', 'type': 'spaceusage', 'value': str(space_usage)+" %"})

        #Freier Speicher
        free_space, free_space_label = self.get_free_space_data()
        systeminfo.append({'name': 'Freier Speicher', 'type': 'freespace', 'value': str(free_space)+" "+free_space_label})

        #RAM-Auslastung
        ram_usage = psutil.virtual_memory().percent
        systeminfo.append({'name': 'RAM-Nutzung', 'type': 'ramusage', 'value': str(ram_usage)+" %"})

        return systeminfo