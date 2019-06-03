import zmq
import time
import json
import sys
import argparse


def _xerces_exists():
    """ Check if xerces wrapper is installed

    Returns:

    """
    try:
        __import__('xerces_wrapper')
    except ImportError:
        print "XERCES DOES NOT EXIST"
        return False
    else:
        print "XERCES EXISTS"
        return True


def _xerces_validate_xsd(xsd_string):
    """ Validate schema using Xerces

    Args:
        xsd_string:

    Returns:
        errors

    """
    if _xerces_exists():
        import xerces_wrapper
        print "XERCES IMPORTED"
        error = xerces_wrapper.validate_xsd(xsd_string)
        print "SCHEMA validated"
        if len(error) <= 1:
            print "SCHEMA valid"
            error = None

        return error
    else:
        return "Xerces is not installed"


def _xerces_validate_xml(xsd_string, xml_string):
    """ Validate document using Xerces

    Args:
        xsd_string:
        xml_string:

    Returns:
        errors

    """
    if _xerces_exists():
        import xerces_wrapper
        print "XERCES IMPORTED"
        error = xerces_wrapper.validate_xml(xsd_string, xml_string)
        print "DATA validated"
        if len(error) <= 1:
            print "DATA valid"
            error = None

        return error
    else:
        return "Xerces is not installed"


def main(argv):
    parser = argparse.ArgumentParser(description="Launch Server Tool")

    # add optional arguments
    parser.add_argument('-e',
                        '--endpoint',
                        help='Listening endpoint',
                        nargs=1,
                        required=True)

    parser.add_argument('-c',
                        '--contextzmq',
                        help='Context zmq',
                        nargs=1,
                        required=True)

    # parse arguments
    args = parser.parse_args()

    # get optional arguments
    if args.endpoint:
        endpoint = args.endpoint[0]
    else:
        endpoint = 'tcp://127.0.0.1:5555'

    if args.contextzmq:
        context_zmq = int(args.contextzmq[0])
    else:
        context_zmq = 7

    # socket configuration
    context = zmq.Context(context_zmq)
    socket = context.socket(zmq.REP)
    socket.bind(endpoint)

    mutex = True
    while True:
        if mutex:
            #  Wait for next request from client
            message = socket.recv()
            print "Received request"

            try:
                message = json.loads(message)

                # validate data against schema
                if 'xml_string' in message:
                    print "VALIDATE XML"
                    mutex = False
                    try:
                        xsd_string = message['xsd_string'].encode('utf-8')
                    except:
                        xsd_string = message['xsd_string']

                    try:
                        xml_string = message['xml_string'].encode('utf-8')
                    except:
                        xml_string = message['xml_string']

                    error = _xerces_validate_xml(xsd_string, xml_string)

                    if error is None:
                        error = 'ok'

                    response = error
                else:
                    print "VALIDATE XSD"
                    mutex = False
                    try:
                        xsd_string = message['xsd_string'].encode('utf-8')
                    except:
                        xsd_string = message['xsd_string']

                    error = _xerces_validate_xsd(xsd_string)

                    if error is None:
                        error = 'ok'

                    response = error

                print response

                socket.send(str(response))
                mutex = True
                print "Sent response"
            except Exception, e:
                print e.message
                pass

        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])


