import subprocess as sp
import os

os.system('sudo sh -c \'echo " #!/usr/bin/env xdg-open\
[Desktop Entry]\
Type=Application\
Terminal=false\
Exec=/usr/bin/google-chrome\
Name=Google Chrome\
Icon=/usr/share/icons/hicolor/48x48/apps/google-chrome.png" > ~/Desktop/chrome.desktop\'')
os.system('chmod +x ~/Desktop/chrome.desktop')
os.system('mv ~/Desktop/chrome.desktop ~/.local/share/applications/')
