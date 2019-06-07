# TODO: There's bound to be a better way to do this
from EzElb import EzElb
from EzElb_0_3 import EzElb as EzElb03
from EzElb_0_4 import EzElb as EzElb04

name = "ez_elb"

EZ_ELB_VERSIONS = {
    "0.5": lambda: EzElb,
    "0.4": lambda: EzElb04,
    "0.3": lambda: EzElb03
}


def ez_elb(version):
    if version not in EZ_ELB_VERSIONS:
        raise Exception("unknown EzElb version: " + version)
    return EZ_ELB_VERSIONS[version]()
