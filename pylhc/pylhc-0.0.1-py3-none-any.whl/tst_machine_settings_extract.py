import logging
from print_machine_settings_overview import main, setup_logger

LOG = logging.getLogger(__name__)
setup_logger()


main(
    time="2018-07-24 10:15:00.000",
    knobs=[
        # "LHCBEAM/IP1-XING-H-MURAD",
        "LHCBEAM/IP1-XING-V-MURAD",
        "LHCBEAM/IP2-XING-V-MURAD",
        "LHCBEAM/IP5-XING-H-MURAD",
        # "LHCBEAM/IP5-XING-V-MURAD",
        "LHCBEAM/IP8-XING-H-MURAD",

        "LHCBEAM/IP1-SEP-H-MM",
        # "LHCBEAM/IP1-SEP-V-MM",
        "LHCBEAM/IP2-SEP-H-MM",
        # "LHCBEAM/IP5-SEP-H-MM",
        "LHCBEAM/IP5-SEP-V-MM",
        "LHCBEAM/IP8-SEP-V-MM",

        # "LHCBEAM/IP5-OFFSET-V-MM",
    ],)
