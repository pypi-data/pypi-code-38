import os
import subprocess as sp

def installation_swa(envTag):
    os.system("sudo docker pull xseed/max-swa:%s" %envTag)
    os.system("sudo docker stop max_swa")
    os.system("sudo docker rm max_swa")
    os.system("sudo docker rmi xseed/max-swa:current")
    os.system("sudo docker tag xseed/max-swa:%s xseed/max-swa:current" %envTag)
    os.system("sudo docker rmi xseed/max-swa:%s" %envTag)
    os.system("sudo docker-compose run -d --service-ports --name max_swa swa")

def installation_minicampus(envTag):
    os.system("sudo docker pull xseed/max-minicampus:%s" %envTag)
    os.system("sudo docker stop max_minicampus")
    os.system("sudo docker rm max_minicampus")
    os.system("sudo docker rmi xseed/max-minicampus:current")
    os.system("sudo docker tag xseed/max-minicampus:%s xseed/max-minicampus:current" %envTag)
    os.system("sudo docker rmi xseed/max-minicampus:%s" %envTag)
    os.system("sudo docker-compose run -d --service-ports --name max_minicampus minicampus")

def installation_backend(envTag):
    os.system("sudo docker pull xseed/max-backend:%s"%envTag)
    os.system("sudo docker stop max_backend")
    os.system("sudo docker rm max_backend")
    os.system("sudo docker rmi xseed/max-backend:current")
    os.system("sudo docker tag xseed/max-backend:%s xseed/max-backend:current" %envTag)
    os.system("sudo docker rmi xseed/max-backend:%s" %envTag)
    os.system("sudo docker-compose run -d --service-ports --name max_backend backend")

def installation_assessment(envTag):
    os.system("sudo docker pull xseed/max-assessment:%s" %envTag)
    os.system("sudo docker stop max_assessment")
    os.system("sudo docker rm max_assessment")
    os.system("sudo docker rmi xseed/max-assessment:current")
    os.system("sudo docker tag xseed/max-assessment:%s xseed/max-assessment:current" %envTag)
    os.system("sudo docker rmi xseed/max-assessment:%s" %envTag)
    os.system("sudo docker-compose run -d --service-ports --name max_assessment assessment")

def installation_complete(envTag):
    installation_backend(envTag)
    installation_minicampus(envTag)
    installation_swa(envTag)
    installation_assessment(envTag)


def installBuilds(userInput, envTag):
    if userInput == 1:
        installation_complete(envTag)
    elif userInput == 2:
        installation_minicampus(envTag)
    elif userInput == 3:
        installation_backend(envTag)
    elif userInput == 4:
        installation_swa(envTag)
    elif userInput == 5:
        installation_assessment(envTag)

def getUserInput(buildEnv):
    if(buildEnv == 'staging'):
        envTag = 'staging'
    else:
        envTag = 'latest'
    os.system("cd /var/www")

    #Code to select build download location
    os.system("printf \"##########################################################\n\
    ######### Welcome to Docker container installation/updation ###########\n\
    ##########################################################\n\
    Please select operation: \n\n\
    Option #1 : Installation/Updation of All 4 apps \n\
    Option #2 : Installation/Updation of MAX Minicampus Front End App\n\
    Option #3 : Installation/Updation of Backend code\n\
    Option #4 : Installation/Updation of SWA App\n\
    Option #5 : Installation/Updation of Assessment App\n\
    ########################################################## \n\"")

    #Code to select operation and execute the respective option
    while True:
        userInput = int(input("Enter option #: \n"))
        if userInput not in (1,2,3,4,5):
            print("ERROR: Entered option which is not supported\n\
            Supported range : 1 / 2 / 3 / 4 / 5 \n")
        else:
            break

    try:
        installBuilds(userInput, envTag)
    except OSError:
        print (e.message)
        print ("Exiting the process because of above error")
        exit();
