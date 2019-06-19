import os
import subprocess as sp

def installation_swa():
    os.system("docker pull xseed/max-swa:latest")
    os.system("docker stop max_swa")
    os.system("docker rm max_swa")
    os.system("docker rmi xseed/max-swa:current")
    os.system("docker tag xseed/max-swa:latest xseed/max-swa:current")
    os.system("docker rmi xseed/max-swa:latest')
    os.system("docker-compose run -d --service-ports --name max_swa swa")

def installation_minicampus():
    os.system("docker pull xseed/max-minicampus:latest")
    os.system("docker stop max_minicampus")
    os.system("docker rm max_minicampus")
    os.system("docker rmi xseed/max-minicampus:current")
    os.system("docker tag xseed/max-minicampus:latest xseed/max-minicampus:current")
    os.system("docker rmi xseed/max-minicampus:latest")
    os.system("docker-compose run -d --service-ports --name max_minicampus minicampus")

def installation_backend():
    os.system("docker pull xseed/max-backend:latest")
    os.system("docker stop max_backend")
    os.system("docker rm max_backend")
    os.system("docker rmi xseed/max-backend:current")
    os.system("docker tag xseed/max-backend:latest xseed/max-backend:current")
    os.system("docker rmi xseed/max-backend:latest")
    os.system("docker-compose run -d --service-ports --name max_backend backend")

def installation_assessment():
    os.system("docker pull xseed/max-assessment:latest")
    os.system("docker stop max_assessment")
    os.system("docker rm max_assessment")
    os.system("docker rmi xseed/max-assessment:current")
    os.system("docker tag xseed/max-assessment:latest xseed/max-assessment:current")
    os.system("docker rmi xseed/max-assessment:latest")
    os.system("docker-compose run -d --service-ports --name max_assessment assessment")

def installation_complete():
    installation_backend()
    installation_minicampus()
    installation_swa()
    installation_assessment()


def switch(userInput):
    switcher = {
    1: installation_complete(),
    2: installation_minicampus(),
    3: installation_backend(),
    4: installation_swa(),
    5: installation_assessment()
    }
    print switcher.get(userInput, "ERROR: Entered option which is not supported\n\
    Supported range : 1 / 2 / 3 / 4 / 5 \n")

os.system("sudo cd /var/www")

#Code to select build download location
os.system("printf \"##########################################################\n\
######### Welcome to Docker container installation/updation  ##############\n\
##########################################################\n\n\
Please select operation: \n\n\
Option #1 : Installation/Updation of All 4 apps \n\
Option #2 : Installation/Updation of MAX Minicampus Front End App\n\
Option #3 : Installation/Updation of Backend code\n\
Option #4 : Installation/Updation of SWA App\n\
Option #5 : Installation/Updation of Assessment App\n\
########################################################## \n \n\"

#Code to select operation and execute the respective option
userInput = int(input("'Enter option #: \n"))
switch(userInput)
