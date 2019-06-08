# -*-coding: utf8;-*-

#####################\
# XRDownloader v1.0.5
#####################/

#----------------------------------------------------------------------------
# MIT License

# Copyright (c) 2019 XploitsR

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#------------------------------------------------------------------------------
try:
 import os,time
 import sys,re
 from .xrUrllib3Conf import xrUrllib3
 from .resume import resume_download
 from .banner import banner
 from .convert import convert_byte
except (ImportError,Exception) as e:
 print(e)
 quit()

# count number of lines in the file links file
def rawincount(filename):
    num_lines = 0
    with open(filename) as f:
      for line in f:
        if len(line.strip()) < 1:
          continue
        else:
          num_lines += 1
    return num_lines

# print preparing to download
def pre(arg):
  os.system("clear")
  banner()
  time.sleep(2)
  print("""
[=============================================================]
        [*] Preparing to download-->({0})->file(s)
[=============================================================]
""".format(arg))
  time.sleep(2)

# write all links to a file
def write_all_links(url):
   with open("allXlinks.txt","a") as f:
      f.write(url + "\n") 
      f.close()

# write fetched data with No ['Content-Length'] to a file
def write_to_fileNoL(url_split,typeO,dataData):
    print("""
[================] 
   please wait
[================]
""")
    with open(url_split,typeO) as f:
      if f is not None:
        for dataNoContentLength in dataData:
          f.write(dataNoContentLength)
        if dataNoContentLength is not None:
          print("[+] downloaded->{0}".format(url_split))
          f.close()

# write fetched data with ['Content-Length'] to a file
def write_to_fileYhL(dataHeader,url_split,typeO,dataStream):
   import math
   from tqdm import tqdm
   total_size = dataHeader
   block_size = 1000
   wrote = 0
   print(" ")
   print("File size: {0}".format(convert_byte(total_size)[0]))
   # write downloaded file to its named-file on same directory
   with open(str(url_split),typeO) as f:
     if f is not None:
         for cont in tqdm(dataStream,total=math.ceil(total_size//block_size),\
            unit=convert_byte(total_size)[1],unit_scale=True):
            wrote = wrote  + len(cont)    
            f.write(cont)
         if total_size != 0 and wrote == total_size:
           print("[+] downloaded->{0}".format(str(url_split)))
           f.close()

def main(xrurl,typeO):
        """
        Contains all functions
        """
        # check for empty value
        if len(str(xrurl)) < 1:
           time.sleep(2)
           print("""
[=============================================================]
           [!] Don't be silly, url cant be empty.
[=============================================================]
""")
           sys.exit()
        # check if input is not a list
        if type(xrurl) != list:
           try:  
            check_usrF = os.path.isfile(xrurl)
           except:
            check_usrF = False
           # check if xrurl is a file
           if check_usrF == True:
              f = open(str(xrurl).strip())
              if len(str(f).strip()) > 1:
                if rawincount(xrurl) == 0:
                  time.sleep(2)
                  print("""
[=============================================================]
           [!] Don't be silly, file cant be empty.
[=============================================================]
""")
                  sys.exit()
                else:
                 pre(rawincount(xrurl))
                 xrurl = f
           else:
              pre(len([xrurl]))
              xrurl = [xrurl]
        # check if input is exact... list
        elif type(xrurl) == list:
           pre(len(xrurl))
           xrurl = xrurl
        count = 0
        # start iterating the urls
        for url in xrurl:
          # convert url to string -> str:
          url = str(url)
          # trim all whitescpaces and \n,\t,\r,\a
          trimmed = False
          while trimmed == False:
           pos = url.find("  ")
           pos_2 = url.find("\t")
           pos_3 = url.find("\r")
           pos_4 = url.find("\a")
           pos_5 = url.find("\n")
           if pos != -1 or pos_2 != -1 or \
            pos_3 != -1 or pos_4 != -1 or \
            pos_5 != -1:
            url = url.replace(" ","")
            url = url.replace("\n","")
            url = url.replace("\t","")
            url = url.replace("\r","")
            url = url.replace("\a","")
           else:
            trimmed = True
          # jump/run over newlines
          if len(url.strip()) < 1:
             continue
          url_split = str(url.strip()).split("/")
          chk_git = str(url_split[-1]).lower().split(".")
          if chk_git[-1] == "git":
             print("""
[=============================================================]
        [!] Don't be silly, can't download git files
[=============================================================]
""")
             print("[!] please download git files with (git clone) command in your terminal")
             sys.exit()
          count += 1
          # check for invalid link type
          if len(str(url_split[-1]).strip()) < 1:
             url_split[-1] = "{0}-unknown-file".format("-".join(url_split))
          print("""
[=============================================================]
        [+] Downloading-->{0}-->({1})                      
[=============================================================]
                """.format(str(url_split[-1][:20] + (url_split[-1][20:] and '...')),count))
          http = xrUrllib3()
          data = http.request('GET',url,preload_content=False) 
          # 200 means succeeded in connecting to site
          if data.status == 200:
           if str(url.strip()) is not None:
            # check if file downloading already exists
            check_Fexists = os.path.exists(str(url_split[-1]))
            if check_Fexists == True:
               resume = resume_download(url.strip(),str(url_split[-1]),http,data,"ab")
               if resume == False:  
                 while True:
                   print("[!] {0} file already exists".format(str(url_split[-1])))
                   print("[>] please do you want to overwrite it? yes/no")
                   if sys.version_info[0] < 3:
                     usr = str(raw_input("[#] >>>: "))
                   else:
                     usr = str(input("[#] >>>: "))
                   # verify user input choice
                   if len(usr.strip()) > 0 and usr.lower().strip() == "yes":
                      print("[O] ok->Overwriting({0})".format(str(url_split[-1])))
                      start = True
                      break
                   elif len(usr.strip()) > 0 and usr.lower().strip() == "no":
                      print("[>] Or do you want to rename it? yes/no")
                      if sys.version_info[0] < 3:
                        usr = str(raw_input("[#] >>>: "))
                      else:
                        usr = str(input("[#] >>>: "))
                      if len(usr.strip()) > 0 and usr.lower().strip() == "yes":
                         try:
                          # Generate random alphanumeric char
                          import uuid
                         except:
                          print("sorry, uuid module not found..please install it")
                          sys.exit()
                         ranNum = str(uuid.uuid4()).split("-")[1]
                         url_split[-1] = "{0}-{1}".format(ranNum,url_split[-1])
                         start = True
                         break
                      elif len(usr.strip()) > 0 and usr.lower().strip() == "no":
                         print("[S] ok->Skipped({0})".format(str(url_split[-1])))
                         start = False
                         break
                         
                      else:
                         print("[!] Don't be silly, choose from above list")
                         time.sleep(2)
                         print(" ")
                   else:
                      print("[!] Don't be silly, choose from above list")
                      time.sleep(2)
                      print(" ")

                 # procced if yes
                 if start == True:
                   write_all_links(url)
                   if 'Content-Length' not in data.headers:
                     # check desc above ;)
                     write_to_fileNoL(str(url_split[-1]),typeO,data.stream(1000))
                   else:
                     try:
                       # check desc above ;)
                       write_to_fileYhL(int(data.headers['Content-Length']),url_split[-1],typeO,data.stream(1000))
                     except (RuntimeError,KeyboardInterrupt,Exception) as e:
                       print("[!] Something unexpectedly happened->Exiting...")
                       sys.exit()
            else:
                write_all_links(url)
                if 'Content-Length' not in data.headers:
                  # check desc above ;)
                  write_to_fileNoL(str(url_split[-1]),typeO,data.stream(1000))
                else:
                  try:
                    # check desc above ;)
                    write_to_fileYhL(int(data.headers['Content-Length']),url_split[-1],typeO,data.stream(1000))
                  except (RuntimeError,KeyboardInterrupt,Exception) as e:
                    print("[!] Something unexpectedly happened->Exiting...")
                    sys.exit()

          # HTTPError: 404 means..file not found
          elif data.status == 404:
           print("[!] DownloadError: File not found")
           continue

          elif data.status == 403:
           print("[!] HTTPError: Access to the requested (valid) URL is Forbidden")
           continue

          # if any other http error occures, exit program
          else:
           print("[!] HTTPError: Couldn't fetch data,retry ")
           continue

if __name__ == '__main__':
   sys.exit()
