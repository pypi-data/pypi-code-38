
import pypci

from . import gpg2000
from . import gpg6204
from . import gpg7204

from . import pci2702
from . import pci2724
from . import pci3165
from . import pci3177
from . import pci3342
from . import pci340816
from . import pci340516
from . import pci6204
from . import pci7204
from . import pci7415v

interface_vendor_id = 0x1147


def open(board_name, board_id):    
    if type(board_id) == int:
        board_id = format(board_id, '1X')
        pass
    
    board_list = pypci.lspci(interface_vendor_id, board_name)
    
    if board_list == []:
        msg = 'board_id {0} is not found'.format(board_name)
        raise TypeError(msg)
    
    for board in board_list:
        if board_name == 2702:
            b = pci2702.pci2702_driver(board)
            if b.board_id == board_id:
                return gpg2000.gpg2000(b)
            pass
        
        if board_name == 2724:
            b = pci2724.pci2724_driver(board)
            if b.board_id == board_id:
                return gpg2000.gpg2000(b)
            pass
        
        if board_name == 3165:
            # temporary
            b = pci3165.pci3165_driver(board)
            if b.board_id == board_id:
                return b
            pass
        
        if board_name == 3177:
            b = pci3177.pci3177_driver(board)
            if b.board_id == board_id:
                return b
            pass

        if board_name == 3342:
            # temporary
            b = pci3342.pci3342_driver(board)
            if b.board_id == board_id:
                return b
            pass
        
        if board_name == 3408:
            b = pci340816.pci340816_driver(board)
            if b.board_id == board_id:
                return b
            pass

        if board_name == 3405:
            b = pci340516.pci340516_driver(board)
            if b.board_id == board_id:
                return b
            pass
        
        if board_name == 6204:
            b = pci6204.pci6204_driver(board)
            if b.board_id == board_id:
                return gpg6204.gpg6204(b)
            pass

        if board_name == 7204:
            b = pci7204.pci7204_driver(board)
            if b.board_id == board_id:
                return gpg7204.gpg7204(b)
            pass

        if board_name == 7415:
            b = pci7415v.pci7415v_driver(board)
            if b.board_id == board_id:
                return b
            pass

        continue


