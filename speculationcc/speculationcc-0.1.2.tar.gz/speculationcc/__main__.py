from speculationcc import sentiment
import getopt, sys, os

def main(args=None):
    """The main routine."""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdf:v", ["help","data=","file="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    data = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-d", "--data"):
            data = a
        elif o in ("-f", "--file") and os.path.isfile(a):
            data = open(a, "r").read()
        else:
            assert False, "unhandled option"
    # text = 'The beauty and elegance of this implementation simply demands that it be packaged properly for distribution.'
    s = sentiment.get_sentiment_from_text(data)
    if s != None:
        print("sentiment:% 6.3f" %(s))

if __name__ == "__main__":
    main()

def usage():
    print "speculationcc -data \"Sentiment test\""
