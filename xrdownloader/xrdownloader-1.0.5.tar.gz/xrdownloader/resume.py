# -*-coding: utf8;-*-
try:
 from .xrUrllib3Conf import xrUrllib3
 from tqdm import tqdm
 from .convert import convert_byte
 import os,sys,math,time
except (ImportError,Exception) as e:
 print(e)
 quit()

def resume_download(url,url_split,http,dataD,typeO):
  """ Resume file function """
  try:
   http = http
   data = dataD
   # check for content in data header
   if 'Content-Length' not in data.headers:
    print("[!] ResumeError: Can't resume this file-->Overwrite it")
    return False
   # proceed and check for local and net file size
   local_file_size = int(os.path.getsize(url_split))
   url_file_size = int(data.headers['Content-Length'])
   if int(local_file_size) >= url_file_size or int(local_file_size) == 0:
     return False
   print("[==[.]file already exists, but ---> broken / unupdated==]")
   print("""
[=============================================================]
     [*] Preparing to resume / update-->({0})
[=============================================================]
""".format(url_split[:20] + (url_split[20:] and '...'))) # shorten longer urls
   # send resume bytes
   user_agent = { 'range':'bytes={0}-{1}'.format(local_file_size,url_file_size) }
   data = http.request('GET',url,preload_content=False,headers=user_agent)
   block_size = 1000
   wrote = 0
   total_size_split = str(data.headers['Content-Range']).split(" ")
   total_size = eval(total_size_split[-1])
   print(" ")
   # print file size
   print("[=] File size: {0}".format(convert_byte(url_file_size)[0]))
   print("[=] Resume File size: {0}".format(convert_byte(total_size)[0]))
   with open(str(url_split),typeO) as f:
     if f is not None:
      print("""
[=============================================================]
     [+] Resuming / Updating-->({0})                      
[=============================================================]
           """.format(url_split[:20] + (url_split[20:] and '...')))
      try:
       for data in tqdm(data.stream(block_size),total=math.ceil(int(total_size)//block_size),\
        unit=convert_byte(total_size)[1],unit_scale=True):
        wrote = wrote + len(data)
        f.write(data)
      except (RuntimeError,KeyboardInterrupt,Exception):
       print("\n[!] Something unexpectedly happened->Exiting...")
       sys.exit()
      if url_file_size != 0 and wrote >= local_file_size:
       print("[+] downloaded->{0}".format(str(url_split)))
       f.close()
  except Exception as e:
   print("[!] ResumeError: Can't resume this file-->Overwrite it")
   return False

if __name__ == '__main__':
   sys.exit()
