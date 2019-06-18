from tests.CSVWriterTest import csvWriterControllerTest
from tests.OFXReaderTest import ofxReaderTest, ofxReaderTestFile
from tests.XMLReaderTest import xmlReaderTestFile
from tests.ProsperarCoreTest import prosperarCoreTest

from controller.AppController import AppController

import logging, sys

logger = logging.getLogger(__name__)

# TODO: passar isso para uma unidade de testes. Manter a main enxuta
def runTests():
    logger.info('running tests')
    #prosperarCoreTest()
    #ofxReaderTest()
    #ofxReaderTestFile()
    #xmlReaderTestFile()
    #csvWriterControllerTest()
    #csvFactoryTest()

def main():
    #logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    #runTests()
    app = AppController()
    app.run()


if __name__ == "__main__":
    main()