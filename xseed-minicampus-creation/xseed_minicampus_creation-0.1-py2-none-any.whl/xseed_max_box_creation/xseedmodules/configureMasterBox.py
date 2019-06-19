import os
import subprocess as sp

def folderEncryption (x):
    try:
     null = open("log.txt", "a")
     sudo_password = x
     command1 = 'apt-get update -y'
     folder="/var/www/xseed-minicampus-frontend/dist/client/en/static/synced/maxVideos"
     mountphrase="pneum@n@u1tramicr@5c@pic5i1ic@v@1can@c@ni@5i5"
     print("Passphrase for customer: %s" %mountphrase)
     sig = os.popen('printf %s| ecryptfs-add-passphrase | tail -1 | awk \'{print $6}\' | sed "s/\[//g" | sed "s/\]//g"' % mountphrase).read()
     command = "sudo mount -t ecryptfs -o key=passphrase:passphrase_passwd=%s,no_sig_cache=yes,verbose=n,ecryptfs_sig=%s,ecryptfs_cipher=aes,ecryptfs_key_bytes=16,ecryptfs_passthrough=n,ecryptfs_enable_filename_crypto=n %s %s" % (mountphrase, sig, folder, folder)
     os.system('sudo mkdir -p %s' %folder)
     os.system('echo %s|sudo -S %s' % (sudo_password, command1))
     os.system('%s' %command)
     os.system('sudo mkdir -p /root/.ecryptfs')
     os.system('sudo sh -c \'echo %s > /root/.ecryptfs/sig-cache.txt\'' %sig)
     os.system('sudo sh -c \'echo "key=passphrase:passphrase_passwd_file=/root/junkpass.txt \
              ecryptfs_sig=%s\
              ecryptfs_cipher=aes\
              ecryptfs_key_bytes=16\
              ecryptfs_passthrough=n\
              ecryptfs_enable_filename_crypto=n" > /root/.ecryptfsrc\'' %sig)
     os.system('sudo sh -c \' echo "passphrase_passwd=%s" > /root/junkpass.txt\'' % mountphrase)
     os.system('sudo sh -c \' echo "%s %s ecryptfs defaults 0 0" >  /etc/fstab\'' %(folder, folder))
     os.system('sudo chown xseed:xseed\
      /var/www/xseed-minicampus-frontend/dist/client/en/static/synced/maxVideos')

    except OSError:
      print (e.message)
      exit()

def nginxConfigurartion (x):
    try:
      sudo_password = x
      command = 'apt-get update -y'
      os.system('echo %s|sudo -S %s' % (sudo_password, command))
      os.system ('echo "server {\
      listen 80 default_server;\
      listen [::]:80 default_server;\
      server_name _;\
      location / {\
      proxy_pass http://127.0.0.1:4000/;\
      }\
      }"| sudo tee \'/etc/nginx/sites-enabled/default_maxApp\' > /dev/null')
      os.system ('echo "server {\
      listen 8080 default_server;\
      server_name _;\
      location / {\
      proxy_pass http://127.0.0.1:4010/;\
      }\
      }" | sudo tee \'/etc/nginx/sites-enabled/default_SWA\' > /dev/null')
      os.system ('echo "server {\
      listen 8090 default_server;\
      server_name _;\
      location/{\
      proxy_pass http://127.0.0.1:4020/;\
      }\
      }" | sudo tee \'/etc/nginx/sites-enabled/default_TestTaker\' > /dev/null')
      os.system('sudo service nginx restart')
      os.system('sudo service nginx status')

    except Exception as e:
      print (e.message)
      exit()

def removeGuestUser (x):
    try:
     sudo_password = x
     command1 = 'apt-get update -y'
     os.system('echo %s|sudo -S %s' % (sudo_password, command))
     os.system('sudo sh -c \'echo "[Seat:*]\nallow-guest=false\n" > /etc/lightdm/lightdm.conf.d/50-no-guest.conf\'')

    except OSError:
      print (e.message)
      exit()


def configure (sudo_password):
    folderEncryption(sudo_password)
    nginxConfigurartion(sudo_password)
    removeGuestUser(sudo_password)
