import logging
logging.basicConfig()

from .cli import main
import sys
sys.exit(main())
