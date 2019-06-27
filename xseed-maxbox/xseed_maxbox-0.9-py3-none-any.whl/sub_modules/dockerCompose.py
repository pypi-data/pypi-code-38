import subprocess as sp
import os
import sys

def createEnvVariable(miniCampus, dbusername, dbpassword, buildEnv):
    os.system('sudo sh -c \'echo "MINICAMPUS_CODE=%s\
    MONGO_INITDB_ROOT_USERNAME=%s\
    MONGO_INITDB_ROOT_PASSWORD=%s \
    BUILD_ENV=%s\' > /var/www/.env' %(miniCampus, dbusername, dbpassword, buildEnv))

def updatingDockerComposeFile():
    pkgdir = sys.modules['xseed_maxbox'].__path__[0]
    fullpath = os.path.join(pkgdir,"data/docker-compose.yml" )
    os.system('sudo cp %s /var/www/' %fullpath)

def dockerLogin(userName, passWord):
    os.system("docker login --username %s --password %s" %(userName, passWord))

def configureDocker(miniCampus, dbusername, dbpassword, dockerusername, dockerpassword, buildEnv):
    createEnvVariable(miniCampus, dbusername, dbpassword, buildEnv)
    updatingDockerComposeFile()
    dockerLogin(dockerusername, dockerpassword)
