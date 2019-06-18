from factory.OFXReaderFactory import OFXReaderFactory

from factory.CSVWriterFactory import CSVWriterFactory
from factory.XLSMWriterFactory import XLSMWriterFactory

import logging

logger = logging.getLogger(__name__)

class ProsperarCore():
    def run(self, file):
        #ler o caminho do arquivo e verificar se ele existe
        if (file is None):
            logger.info('No file specified.')
            return

        #chamar o leitor ofx
        factoryOFX = OFXReaderFactory()
        readerController = factoryOFX.createReaderController()
        bs = readerController.read(factoryOFX, file=file)

        #chamar o escritor xlsm
        factory = XLSMWriterFactory()
        writerController = factory.createWriterController()
        return writerController.write(bs, factory)