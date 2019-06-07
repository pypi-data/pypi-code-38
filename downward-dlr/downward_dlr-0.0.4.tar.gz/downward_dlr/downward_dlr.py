#author: Christoph Suerig
#date: 06.06.2019
#This is the main file of downward-dlr
#it was adding the argument "--build" to argv in previous versions when it was needed.
#now its just for Backward compatibility.

def dwdlr_main():
    from .driver.main import main
    main()

