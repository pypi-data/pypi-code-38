# -*-coding: utf8;-*-
try:
  import sys
  import pyfiglet
except (ImportError,Exception) as e:
  print(e)
  quit()

try:
  # xrdownloader's banner
  def banner():
   print(pyfiglet.figlet_format("XRDOWNLOADER", font='slant'))
except:
  def banner():
   print("""
[=======================]
 #     XRDOWNLOADER    #
[=======================]
""")

if __name__ == '__main__':
   sys.exit()
