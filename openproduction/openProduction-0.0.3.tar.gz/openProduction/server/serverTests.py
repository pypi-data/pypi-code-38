from openProduction.server import ServerInterface
from openProduction.connectors.BaseConnector import ConnectorErrors
import time
from random import randint

wdir = r"C:\Users\Markus\AppData\Local\pieye\openProduction"
workspace = "testing"
s = ServerInterface.ServerInterface.create(wdir)

#%%
s.deleteWorkspace(workspace)
start = time.time()
rv = s.createWorkspace(workspace)
print(rv, time.time() - start)



start = time.time()
data = {"name": "klebestation", "description": "Klebestation"}
rv = s.createStation(data)
print(rv, time.time() - start)

start = time.time()
data = {"git_url": "https://dev.pieye.org/source/openProductionTestRepo.git", "git_username": "openProduction", "git_password": "CarlSchnitzel19",
        "git_usermail": "noreply@pieye.org"}
rv = s.createGitCredentials(data)
print(rv, time.time() - start)

#PRODUKT erstellen
start = time.time()
data = {"name": "Bauernstolz", "description": "Bauernstolz in allen Varianten"}
stationLink = {"station_id": 1, "order": 1}
rv = s.createProduct(data, stationLink)
print(rv, time.time() - start)

#PRODUKT Revision erstellen
start = time.time()
f = open(r"C:\Users\Markus\Downloads\devImage2.png", "rb")
img = f.read()
f.close()
data = {"product_id": 1, "version": "AA", "git_credential_id": 1,
        "git_branch": "bauernstolz", "description": "erste Version Klebeplatz", "image": img, "station_id": 1}
revision = {"params": {"param1": "test"}, "commit_id": "f02911cdd744963b2b19eec778457594ee70c5c2"}
rv = s.createProductStep(data, revision)
print(rv, time.time() - start)


#%%
rv = s.updateProductRevisionByName("klebestation", "Bauernstolz", "AA", {"commit_id": "e721510d5b7284834b7e483e80adb5ca7f9b03e8"})
print(rv)


#%%
start = time.time()
rv = s.getProductStepByName("klebestation", "Bauernstolz", "AA")
print(rv[0], time.time() - start)

rvRev = s.getLatestProductRevision(rv[1]["product_step_id"])

#%%

