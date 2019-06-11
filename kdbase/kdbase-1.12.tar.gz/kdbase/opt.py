from optparse import OptionParser

parser = OptionParser()
add_option = parser.add_option
options = None
args = None
argv = None

def set_opt_local():
    global argv # pylint: disable=W0603
    argv = []

def option():
    global options # pylint: disable=W0603
    global args # pylint: disable=W0603
    if not options:
        (options, args) = parser.parse_args(argv)
    return options

DEFINE_FLAG = add_option
FLAG = option

DEFINE_FLAG("-m", "--my_flag",
            action = "store_true",
            dest = "my_flag", default = False,
            help = "Whether to show tag-itemlist")

def main():
    print option().my_flag


if __name__ == '__main__':
    main()
