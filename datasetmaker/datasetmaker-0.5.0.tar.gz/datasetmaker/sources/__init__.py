from .mynewsflash import MyNewsFlash
from .oecd import OECD
# from .skolverket import SKVClient
from .wikipedia import Wikipedia
from .worldbank import WorldBank


available = {
    'mynewsflash': MyNewsFlash,
    'oecd': OECD,
    # 'skolverket': SKVClient,
    'wikipedia': Wikipedia,
    'worldbank': WorldBank
}
