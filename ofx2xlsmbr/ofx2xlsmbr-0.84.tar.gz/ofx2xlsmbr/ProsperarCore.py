from .factory.OFXReaderFactory import OFXReaderFactory
from .factory.XLSMWriterFactory import XLSMWriterFactory

import logging

logger = logging.getLogger(__name__)

class ProsperarCore():
    def run(self, files):
        #ler o caminho do arquivo e verificar se ele existe
        if (files is None):
            logger.info('No files specified.')
            return

        #chamar o leitor ofx
        factoryOFX = OFXReaderFactory()
        readerController = factoryOFX.createReaderController()
        bankStmts = readerController.read(factoryOFX, files=[files])

        #chamar o escritor xlsm
        factory = XLSMWriterFactory()
        writerController = factory.createWriterController()
        return writerController.write(bankStmts[0], factory)