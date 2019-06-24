
import pypci

from . import gpg2000
from . import gpg3100
from . import gpg3300
from . import gpg6204
from . import gpg7204

from . import pci2702
from . import pci2724
from . import pci3165
from . import pci3177
from . import pci3342
from . import pci3346
from . import pci340816
from . import pci340516
from . import pci6204
from . import pci7204
from . import pci7415v

interface_vendor_id = 0x1147


def open2702(pci_config_header):
    driver = pci2702.pci2702_driver(pci_config_header)
    return gpg2000.gpg2000(driver)

def open2724(pci_config_header):
    driver = pci2724.pci2724_driver(pci_config_header)
    return gpg2000.gpg2000(driver)

def open3165(pci_config_header):
    driver = pci3165.pci3165_driver(pci_config_header)
    return driver

def open3177(pci_config_header):
    driver = pci3177.pci3177_driver(pci_config_header)
    return gpg3100.gpg3100(driver)

def open3342(pci_config_header):
    driver = pci3342.pci3342_driver(pci_config_header)
    return driver

def open3346(pci_config_header):
    driver = pci3346.pci3346_driver(pci_config_header)
    return gpg3300.gpg3300(driver)

def open3408(pci_config_header):
    driver = pci340816.pci340816_driver(pci_config_header)
    return driver

def open3405(pci_config_header):
    driver = pci3405.pci3405_driver(pci_config_header)
    return driver

def open6204(pci_config_header):
    driver = pci6204.pci6204_driver(pci_config_header)
    return gpg6204.gpg6204(driver)

def open7204(pci_config_header):
    driver = pci7204.pci7204_driver(pci_config_header)
    return gpg7204.gpg7204(driver)

def open7415(pci_config_header):
    driver = pci7415.pci7415_driver(pci_config_header)
    return driver



open_func = {
    2702: open2702,
    2724: open2724,
    3165: open3165,
    3177: open3177,
    3342: open3342,
    3346: open3346,
    3408: open3408,
    340816: open3408,
    3405: open3405,
    6204: open6204,
    7204: open7204,
    7415: open7415,
}



def open(board_name, board_id):    
    if type(board_id) == int:
        board_id = format(board_id, '1X')
        pass
    
    pci_config_headers = pypci.lspci(interface_vendor_id, board_name)
    
    if pci_config_headers == []:
        msg = 'board_id {0} is not found'.format(board_name)
        raise TypeError(msg)
    
    for conf in pci_config_headers:
        b = open_func[board_name](conf)
        if b.board_id == board_id:
            return b
        continue
    return


def lspci():
    pci_config_headers = pypci.lspci(interface_vendor_id)
    
    if pci_config_headers == []:
        msg = 'board_id {0} is not found'.format(board_name)
        raise TypeError(msg)
    
    board_list = []
    for conf in lpci_config_headers:
        board_name = conf.device_id
        b = open_func[board_name](conf)
        board_list.append({'name': board_name, 'rsw': b.board_id})
        continue
        
    for b in sorted(board_list, key=lambda x: x['name']):
        print('%s : RSW=%s'%(b['name'], b['rsw']))
        continue
    return
