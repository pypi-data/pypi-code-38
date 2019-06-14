#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vpillutl
#
# Created:     19/05/2019
# Copyright:   (c) vpillutl 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import netmiko
from netmiko import ConnectHandler
import time
class nexus1000v():
    def __init__(self):
        pass
    def connect(self,ip,user,password):
        try:
            from netmiko import ConnectHandler
            import paramiko
            self.ip=ip
            self.user=user
            self.password=password
            self.device_type='cisco_nxos'
            vsm = {
                        'device_type': 'cisco_nxos',
                        'ip': ip,
                        'username': user,
                        'password': password,
                        }
            self.net_connect = ConnectHandler(**vsm)
            return
        except Exception as e:
            print("ERROR: {}".format(str(e)))
            return

    def ssh_connection(ip_address, username, password):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(
                hostname=ip_address, username=username, password=password
            )
            print("Successful connection", ip_address)
            remote_connection = ssh_client.invoke_shell()
            # ssh_client.close()
            return ssh_client,remote_connection
        except Exception as e:
            print(str(e))
            ssh_client.close()
            return

    def create_port_profile(self,name,pp_type,vlan):
        #vlan=Vlan ID
        #pp_type=Ethernet/Vethernet
        vlan=str(vlan)
        config_commands = ["port-profile type "+pp_type+" "+name,"switchport mode access", "switchport access vlan "+vlan,"state enabled","no shut","vmware port-group"]
        op=self.net_connect.send_config_set(config_commands)
        print(op)
        return

    def create_port_profile_vxlan(self,name,pp_type,vlan):
        #vlan=Vlan ID
        #pp_type=Ethernet/Vethernet
        vlan=str(vlan)
        config_commands = ["port-profile type "+pp_type+" "+name,"switchport mode access", "switchport access vlan "+vlan,"capability vxlan","state enabled","no shut","vmware port-group"]
        self.net_connect.send_config_set(config_commands)
        return

    def create_port_profile_bd(self,name,pp_type,bd):
        #vlan=Vlan ID
        #pp_type=Ethernet/Vethernet
        config_commands = ["port-profile type "+pp_type+" "+name,"switchport mode access", "switchport access bridge-domain "+bd,"state enabled","no shut","vmware port-group"]
        self.net_connect.send_config_set(config_commands)
        return

    def delete_port_profile(self,name):
        config_commands=["no port-profile "+name]
        self.net_connect.send_config_set(config_commands)
        return

    def shut_port_profile(self,name):
        config_commands = ["port-profile "+name,"shut"]
        self.net_connect.send_config_set(config_commands)
        return

    def no_shut_port_profile(self,name):
        config_commands = ["port-profile "+name,"no shut"]
        self.net_connect.send_config_set(config_commands)
        return

    def enable_feature(self,name):
        config_commands=["feature "+name]
        self.net_connect.send_config_set(config_commands)
        return

    def disable_feature(self,name):
        config_commands=["no feature "+name]
        self.net_connect.send_config_set(config_commands)
        return

    def create_vlan(self,vlanID):
        config_commands=["vlan "+vlanID,"state active","no shut"]
        return

    def delete_vlan(self,vlanID):
        config_commands=["no vlan "+vlanID]
        return

    def create_port_profile_bulk(self,pp_type,number,vlan_start):
        for i in range(0,number):
            name="pp_"+vlan_start
            config_commands = ["port-profile type "+pp_type+name,"switchport mode access", "switchport access vlan "+vlan,"state enabled","no shut"]
            self.net_connect.send_config_set(config_commands)
            vlan_start+=1
        return

    def image_change(self,system,kickstart):
        #system=System image path
        #kickstart=Kickstart image path
        ssh_client,remote_connection=ssh_connection(self.ip, self.user, self.password)
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(
            system, "n1000v-dk9-NEW-BUILD.5.2.1.SV3.4.1a.bin"
        )
        sftp_client.put(
            kickstart, "n1000v-dk9-kickstart-NEW-BUILD.5.2.1.SV3.4.1a.bin"
        )
        sftp_client.close()

        print("Images uploaded on vsm")
        system_command = (
            "boot system bootflash:n1000v-dk9-NEW-BUILD.5.2.1.SV3.4.1a.bin"
        )
        kickstart_command = "boot kickstart bootflash:n1000v-dk9-kickstart-NEW-BUILD.5.2.1.SV3.4.1a.bin"
        command_list = [
            "teminal length 0",
            system_command,
            kickstart_command,
            "copy r s",
        ]
        self.net_connect.send_config_set(config_commands)
        remote_connection.send("conf t\n")
        time.sleep(1)
        remote_connection.send("reload\n")
        time.sleep(1)
        remote_connection.send("y\n")
        print(" Switch going for reload now")
        time.sleep(100)
        print("Switch should be back up now")
        connect(self,ip,user,password)
        return

    def switchover(self):
        self.net_connect.send_command("system switchover")
        time.sleep(10)
        initialize(self,ip,user,password)
        op=self.net_connect.send_command("show module")
        return op

    def show(self,command):
        op=self.net_connect.send_command(command)
        print(op)
        return op










