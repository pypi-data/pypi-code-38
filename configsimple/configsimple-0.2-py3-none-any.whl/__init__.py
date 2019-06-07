from .configsimple import ConfigSimple
version = '0.2'

def flag(val):
    val = str(val)
    if val.lower() in ["yes", "true", "y", "t", "1"]:
        return True
    elif val.lower() in ["no", "false", "n", "f", "0"]:
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected, not %s" % (val,))

topconfig = ConfigSimple(component='')
