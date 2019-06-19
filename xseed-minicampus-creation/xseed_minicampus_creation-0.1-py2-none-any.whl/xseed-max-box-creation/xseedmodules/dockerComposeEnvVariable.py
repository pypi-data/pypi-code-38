import subprocess as sp
import os

def createEnvVariable(minicampus):
    os.system('sudo sh -c \'echo "MINICAMPUS_CODE=%s\
    MONGO_INITDB_ROOT_USERNAME=admin123\
    MONGO_INITDB_ROOT_PASSWORD=admin123" > /var/www/.env\'' %miniCampus)

def updatingDockerComposeFile():
    os.system('sudo cp ./docker-compose.yml /var/www/')

def dcokerLogin(userName, passWord):
    os.system("docker login --username %s --password %s" %(userName, passWord))

def configureDocker(miniCampus, username, password):
    createEnvVariable(miniCampus)
    updatingDockerComposeFile()
    dockerLogin(username, password)
