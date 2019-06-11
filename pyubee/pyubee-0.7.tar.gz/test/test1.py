import re
import sys

_WIFI_DEVICES_REGEX = re.compile(
    r'<tr bgcolor=#[0-9a-fA-F]+>'
    r'<td>([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:'
    r'[0-9a-fA-F]{2}:[0-9a-fA-F]{2})</td>'
    r'<td>\d+</td><td>.+</td><td>\d+\.\d+\.\d+\.\d+</td><td>(.+)</td>'
    r'<td>.+</td><td>\d+</td></tr>'
)

_LAN_DEVICES_REGEX = re.compile(
    r'<tr bgcolor=#[0-9a-fA-F]+>'
    r'<td>([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:'
    r'[0-9a-fA-F]{2}:[0-9a-fA-F]{2})</td>'
    r'<td>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}</td>()'
)

_STRING = """
<div id="navigation_bar">
	  <ul>
			<li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeLanSetup.asp" id="ID_A_LAN">LAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWanStatus.asp" id="ID_A_WAN" >WAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeWlanBasic.asp" id="ID_A_WLAN">WLAN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_ADVANCED">Advanced</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a class="current" href="UbeeAdvConnectedDevicesList.asp" id="ID_A_CONNECTED_DEVICES_LIST" >Connected Devices</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedOption.asp" id="ID_A_OPTION" >Options</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortForwarding.asp" id="ID_A_PORT_FORWARDING" >Port Forwarding</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedIpFiltering.asp" id="ID_A_IP_FILTER" >IP Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedMacFiltering.asp" id="ID_A_MAC_FILTER" >MAC Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortFiltering.asp" id="ID_A_PORT_FILTER" >Port Filtering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedPortTriggering.asp" id="ID_A_PORT_TRIGGER" >Port Triggering</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedFirewall.asp"  id="ID_A_ADV_FIREWALL">Firewall</a></div></div></div></div></li><li><div class="l3box"><div class="l3box-outer"><div class="l3box-inner"><div class="l3box-final"><a href="UbeeAdvancedDmz.asp"  id="ID_A_ADV_DMZ">DMZ</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeManagementBackup.asp"  id="ID_A_MANAGEMENT">Management</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeVpnBasic.asp" id="ID_A_VPN">VPN</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeNasControl.asp" id="ID_A_FILE_SHARING">File Sharing</a></div></div></div></div></li><li><div class="box"><div class="box-outer"><div class="box-inner"><div class="box-final"><a href="UbeeParentalUserSetup.asp" id="ID_A_PARENTAL_CONTROL">Parental Control</a></div></div></div></div></li><div id="version" style="visibility:hidden">1.0</div> 

		      </ul>
			  </div>
			<div id="main_page">
              
<div class="description"><h1 id="ID_H1_ADV_CONNECTED_HEADER_TITLE_2G">Connected Stations of Wireless 2.4G</h1><label id="ID_LABEL_ADV_CONNECTED_HEADER_DESC_2G"> This table allows configuration of the Access Control to the AP as well as status on the connected clients.</label></div>

<table>
  
  <tr valign=top>
   
    <td>
    <table>
      <tr bgcolor=#FF8C00><td>&nbsp;<label id="ID_LABEl_STA_MAC_ADDR_2G">MAC Address</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEl_STA_AGE_2G">Age(s)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_RSSI_2G">RSSI(dBm)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_IP_ADDRESS_2G">IP Addr</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_HOSTNAME_2G">Host Name</label>&nbsp;</td><td><label id="ID_LABEL_STA_MODE_2G">Mode</label></td><td><Label id="ID_LABEL_STA_SPEED_2G">Speed</label> (kbps)</td></tr><tr bgcolor=#99CCFF><td>C0:EE:FB:E6:FB:3E</td><td>47156</td><td>-48</td><td>192.168.83.101</td><td>OnePlus_3T</td><td>n</td><td>1000</td></tr>
<tr bgcolor=#9999CC><td>7C:49:EB:B1:A7:6A</td><td>83731</td><td>-63</td><td>192.168.83.40</td><td>lumi-gateway-v3_miio98941320</td><td>n</td><td>72222</td></tr>

    </table>
    </td>
  </tr>
</table>
<hr/>
<div class="description"><h1 id="ID_H1_ADV_CONNECTED_HEADER_TITLE_5G">Connected Stations of Wireless 5G </h1><label id="ID_LABEL_ADV_CONNECTED_HEADER_DESC_5G" > This table allows configuration of the Access Control to the AP as well as status on the connected clients.</label></div>
<table>
  
  <tr valign=top>
    
    <td>
    <table>
      <tr bgcolor=#FF8C00><td>&nbsp;<label id="ID_LABEl_STA_MAC_ADDR_5G">MAC Address</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEl_STA_AGE_5G">Age(s)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_RSSI_5G">RSSI(dBm)</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_IP_ADDRESS_5G">IP Addr</label>&nbsp;</td><td>&nbsp;<label id="ID_LABEL_STA_HOSTNAME_5G">Host Name</label>&nbsp;</td><td><label id="ID_LABEL_STA_MODE_5G">Mode</label></td><td><Label id="ID_LABEL_STA_SPEED_5G">Speed</label> (kbps)</td></tr><tr bgcolor=#99CCFF><td>54:2A:A2:F2:41:90</td><td>22753</td><td>-40</td><td>192.168.83.11</td><td>Static IP</td><td>n</td><td>6000</td></tr>
<tr bgcolor=#9999CC><td>94:0E:6B:73:EC:39</td><td>37853</td><td>-56</td><td>192.168.83.104</td><td>HUAWEI_MediaPad_T3_7</td><td>n</td><td>6000</td></tr>

    </table>
    </td>
  </tr>
</table>

            <div class="description">
	    	      <h1 id="ID_H1_HEADER_ADV_CONNECTED_TITLE">Connected Stations of LAN Users</h1>
	    	    <label id="ID_LABEL_ADV_CONNECTED_TITLE_DESC">  This table shows users connected to LAN.</label> 
    	      </div>
	    	 
	    	      <table>
	    	        <br>
	    	        <tr>
	    	          <td><table style="font-family: Helvetica;font-size:14"><tr bgcolor=#FF8C00><td><label id="ID_LABEL_MAC_ADDRESS">MAC Address</label></td><td><label id="ID_LABEL_IP_ADDRESS">IP Address</label><td><label id="ID_LABEL_DURATION">Duration</label></td><td><label id="ID_LABEL_EXPIRES">Expires</label></td></tr>
<tr bgcolor=#99CCFF><td>B8:27:EB:D6:89:23</td><td>192.168.83.5</td><td>D:-- H:-- M:-- S:--</td><td>*** STATIC IP ADDRESS **</td><td align=center></td></tr>
<tr bgcolor=#9999CC><td>44:F0:34:86:A2:A4</td><td>192.168.83.31</td><td>D:00 H:01 M:00 S:00</td><td>Sun Jan 13 11:19:00 2019
</td><td align=center></td></tr>
</table>
</td>
    	            </tr>
	    	        
    	          </table>
</div>

"""

def get_connected_devices():
    DEVICES = _WIFI_DEVICES_REGEX.findall(_STRING) + _LAN_DEVICES_REGEX.findall(_STRING)
    return {
        key: val for key, val in DEVICES
    }


# print(_STRING)
print(get_connected_devices())

