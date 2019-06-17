import sys
import six
import traceback


def rook_test():
    six.print_("[Rookout] Testing connection to agent")

    if '-v' in sys.argv:
        from rook.config import LoggingConfiguration

        LoggingConfiguration.LOG_LEVEL = "DEBUG"
        LoggingConfiguration.LOG_TO_STDERR = True

    try:
        import rook

        rook.start(throw_errors=True)
        success = True
    except:
        six.print_(file=sys.stderr)
        traceback.print_exc()
        six.print_(file=sys.stderr)

        success = False

    if success:
        six.print_("[Rookout] Test Finished Successfully")
        exit(0)
    else:
        six.print_("[Rookout] Test Failed")
        exit(1)


if '__main__' == __name__:
    rook_test()
