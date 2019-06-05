import sys
import os
from . import indexer, replicator
 
def help ():
    print ("usage: delune <command> [<options>]")
    print ("command:")
    print ("  index")
    print ("  replicate")    
    sys.exit ()
     
def main ():    
    try: 
        cmd = sys.argv [1]
    except IndexError:
        help ()
    sys.argv.pop (1)    
    if cmd == "index":
        indexer.main ()
    elif cmd == "replicate":
        replicator.main ()
    else:
        print ("unknown conmand")


if __name__ == "__main__":
    main ()
