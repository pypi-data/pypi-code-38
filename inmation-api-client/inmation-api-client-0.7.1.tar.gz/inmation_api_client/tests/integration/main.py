import asyncio
import os
import sys
from pathlib import Path
p = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
sys.path.append(str(p))
sys.path.append(str(Path(p).parent))

from tests.integration.connect_test import connect_test
from tests.integration.execfunction_readhist_test import execfunction_readhist_test
from tests.integration.execfunction_test import execfunction_test
from tests.integration.read_test import read_test
from tests.integration.readhistoricaldata_test import readhistoricaldata_test
from tests.integration.runscript_test import runscript_test
from tests.integration.write_test import write_test
from tests.integration.subscribe_test import subscribe_test


def main():
    print('\nBEGIN tests...\n')
    connect_test()
    execfunction_readhist_test()
    execfunction_test()
    read_test()
    readhistoricaldata_test()
    runscript_test()
    write_test()
    subscribe_test()
    print('\nEND tests...\n')


if __name__ == '__main__':
    main()
