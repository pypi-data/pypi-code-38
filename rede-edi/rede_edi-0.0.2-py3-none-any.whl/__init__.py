import re

from .eevc import Eevc

from .eevd import Eevd
from .eevd.models import Header
from .eevd.models import ( 
    SalesSummary, TotalPointSales, TotalHolder, TotalFile,
    TotalHolder, DetailsSalesReceipt, DetailsSalesReceiptEcommerce,
    DetailsReceipt, DisaggregationPreDatedSales, LiquidatedPreDatedTransactions,
    AdjustmentsNet, AdjustmentsNetEcommerce )

from .eefi import Eefi

from pprint import pprint

class EdiTypes:
    EEFI= "EEFI"
    EESA= "EESA"
    EEVC= "EEVC"
    EEVD= "EEVD"

def _get_header(filelocation):
    with open(filelocation, 'r') as f:
        for line in f:
            return line

def file_info(filelocation):

    linetype = None
    lineheader = _get_header(filelocation).strip()
 
    print(lineheader)

    if lineheader.rfind('EEVD') > 0:
        file = Eevd(filelocation)
        print(file.info)
        return file.info 

    if lineheader.rfind('EESA') > 0:
        file = Eevc(filelocation)
        print(file.info)

    if lineheader.rfind('EEFI') > 0:
        file = Eefi(filelocation)
        print(file.info)

    if lineheader.rfind('EEVC') > 0:
        print('eevc') 

    
        






