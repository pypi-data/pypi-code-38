# Author: Solomon Narh (XploitsR Author)
# Copyright (c) 2019 XploitsR

"""
module -> Fast Files Downloader (^_^)

===========

=> XRDownloader is a module for faster downloading of files.
=> Very light weight,and highly efficient.
=> Aggressive security.
=> No loop holes.
=> Open source software.
=> Live downloading statistics (progressbar) 
=> Auto resume failed downloads

======
Class:
======

   XRDownloader()

=========
Function:
=========

  download(url or /path/to/links-file)
  ==========================================


======
Usage:
======

     # import xrdownloader module
       import xrdownloader
       
     # call and assign it to a variable
       xr = xrdownloader.XRDownloader()

     # To download single file, just put in the url
 ==> Example: 
       res = xr.download("http://my.co/im.png")
       print(res)

     # To download multiple files, add [] and seperate the links with ,
 ==> Example: 
       res = xr.download(["http://my.co/im.png","http://u.com/i.pdf"])
       print(res)

     # You can also specify a file that contains your links
 ==> Example: 
       res = xr.download("myLinks.txt")
       print(res)
"""    

try:
 import urllib3
 import time,sys,re
 from .xrmain import main
except (ImportError,Exception) as e:
 print(e)
 quit()

__author__ = "Solomon Narh (XploitsR)"

__author_email__ = 'xploitsr@gmail.com'

__docformat__ = 'reStructuredText'

__url__ = 'https://pypi.org/project/xrdownloader'

__version__ = '1.0.5'

__version_info__ = (1,0,1,2,3,4,5)

__version_details__ = '(resume failed downloads) added in version 1.0.5'

class XRDownloader:
   """defined class to call main() function"""
   def download(self,xrurl):
      """
      To download files, call this function
      
      Attributes
      ----------
      xrurl: your files url or path to your files url file
      ==> example: links.txt,anything.txt, ..etc
      """
      try:
        typeO = "wb"
        main(xrurl,typeO)
        pass
      except Exception as e:
        if str(e).lower() == 'write() argument must be str, not bytes':
          typeO = "w"
          main(xrurl,typeO)
        elif re.search('Connection broken',str(urllib3.exceptions.NewConnectionError)):
          print(e)
        elif urllib3.exceptions.NewConnectionError:
          print("[!] ConnectionError: invalid link or network error")
        else:
          print("[!] " + str(e))
          sys.exit()
      except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()
      time.sleep(0.5)
      return "[^] Done (^_^)"

if __name__ == '__main__':
   sys.exit()
