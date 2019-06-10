import argparse
from . import alias, scripts

parser = argparse.ArgumentParser()

"""
awsume-configure --shell bash --alias-file ~/.bashrc --autocomplete-file ~/.bashrc
    - defaults alias and autocomplete file to ~/.bashrc

awsume-configure --shell zsh --alias-file ~/.zshrc --autocomplete-file /usr/local/share/zsh/site-functions
    - defaults alias file to ~/.zshrc and autocomplete file to /usr/local/share/zsh/site-functions

awsume-configure --shell powershell --alias-file ~/.bashrc --autocomplete-file /usr/local/share/zsh/site-functions
    - powershell autocomplete file is `subprocess.Popen(["powershell", "$profile"], stdout=subprocess.PIPE, shell=True).communicate()`

awsume-configure --shell cmd --alias-file ~/.bashrc --autocomplete-file /usr/local/share/zsh/site-functions
    -
"""

def main():
    print('Setting up the alias')
    print('Setting up the autocomplete script')
    print('Please restart your shell')
    alias.main()
