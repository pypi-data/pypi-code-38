'''    
_PPTddXXR4c	AE9B	01	
BpFmWRg0TNk	AE9B	02	
tyQp-qPa0t8	AE9B	03	
z2RXwUKc8bY	AE9B	04	
A3cpp2DKhhI	AE9B	05	
A56fMfThBw4	AE9B	06	
BBK1If-34DU	AE9B	07	
VK1DdRtCMBc	AE9B	08	
yzaz2L4StCQ	AE9B	09	
fb-CYSJ5Wnc	AE9B	10	
6IvAoD8K20g	AE9B	11	
nPlCNkf5hvE	AE9B	12	
mBM6G84asVA	AE9B	13	
9wqYnctWVBI	AE9B	14	
aD85cw7P4c8	AE9B	15	
Eu53YSmEwWk	AE9B	16	
'''
class GHHouseSettings:
    """Setting for Greenhouse Instance"""
    
    #User specific
    HOUSE_ID = "00"
    ROW_ID = "_PPTddXXXX"
    GROUP_ID = "AAAA"
    
class GHGlobalSettings:
    """Setting for Greenhouse service
    """
    URL = "https://prod-62.westus.logic.azure.com:443/workflows/843ea8f27a8a4aa99fcc98b52c64e609/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=frzmlbvs4IcjAeTSJbocrwKbKenhUAq3AnWoxHZezDs"
    VERSION = "2.1"
    
    #Component settings    
    SERVO_CW_POSITION_DC = 10   
    SERVO_CCW_POSITION_DC = 5
