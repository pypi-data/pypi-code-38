import subprocess as sp
import os

def createEnvVariable(miniCampus, dbusername, dbpassword):
    os.system('sudo sh -c \'echo "MINICAMPUS_CODE=%s\
    MONGO_INITDB_ROOT_USERNAME=%s\
    MONGO_INITDB_ROOT_PASSWORD=%s" > /var/www/.env\'' %(miniCampus, dbusername, dbpassword))

def updatingDockerComposeFile():
    os.system('sudo cp ./docker-compose.yml /var/www/')

def dcokerLogin(userName, passWord):
    os.system("docker login --username %s --password %s" %(userName, passWord))

def configureDocker(miniCampus, dbusername, dbpassword, dockerusername, dockerpassword):
    createEnvVariable(miniCampus, dbusername, dbpassword)
    updatingDockerComposeFile()
    dockerLogin(dockerusername, dockerpassword)
