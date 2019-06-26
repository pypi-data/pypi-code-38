from .factory.OFXReaderFactory import OFXReaderFactory
from .factory.XLSReaderFactory import XLSReaderFactory
from .factory.XLSMWriterFactory import XLSMWriterFactory

import logging

logger = logging.getLogger(__name__)

class ProsperarCore():
    def run(self, files):
        #ler o caminho do arquivo e verificar se ele existe
        if (not files):
            logger.info('No files specified.')
            return

        xlsFiles = []
        ofxFiles = []

        for file in files:
            if ('.xls' in file.name):
                xlsFiles.append(file)
            else:
                ofxFiles.append(file)

        #chamar o leitor ofx
        factoryOFX = OFXReaderFactory()
        readerController = factoryOFX.createReaderController()
        ofxBankStmts = readerController.read(factoryOFX, files=ofxFiles)

        #chamar o leitor xls
        factoryXLS = XLSReaderFactory()
        readerController = factoryXLS.createReaderController()
        xlsBankStmts = readerController.read(factoryXLS, files=xlsFiles)

        bankStmts = xlsBankStmts + ofxBankStmts

        #chamar o escritor xlsm
        factory = XLSMWriterFactory()
        writerController = factory.createWriterController()
        return writerController.write(bankStmts, factory)