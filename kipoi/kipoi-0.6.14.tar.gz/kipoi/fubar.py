import os.path

absp = "/home/thorsten/"
os.chdir(absp)

print(os.getcwd())

print(os.path.expanduser(absp))

os.chdir(os.path.abspath('src'))
print(os.getcwd())




 /root/repo/example/models/extended_coda/example_files/example/models/extended_coda/example_files  
 newdir init example/models/extended_coda/example_files