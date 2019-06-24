import logging
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))

formatter1 = logging.Formatter(
    fmt="%(filename)s line %(lineno)s - %(levelname)s: %(message)s"
)
formatter2 = logging.Formatter(
    fmt="%(asctime)s | %(filename)s line %(lineno)s - %(levelname)s: %(message)s"
)

log = logging.getLogger("dhd")
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter1)

fh = logging.FileHandler(os.path.join(here, "log.log"), mode="w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter2)

log.addHandler(ch)
log.addHandler(fh)
