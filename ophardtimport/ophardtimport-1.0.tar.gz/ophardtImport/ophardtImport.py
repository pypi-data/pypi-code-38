from .models import Fencer, Tournament
from zipfile import ZipFile
import xmltodict
from datetime import datetime
from collections import OrderedDict
from PIL import Image


class OphardtImporter:
    """Imports ophardt exports"""
    tournaments = []
    fencers = []

    def __init__(self, file: ZipFile):
        self.file = file
        self.fileList = []
        for file in self.file.namelist():
            self.fileList.append({'splitted': str(file).split('/'), 'complete': file})

    def get_data(self) -> dict:
        for file in self.fileList:
            if file['splitted'][0] == "XML":
                x = xmltodict.parse(self.file.open(file['complete']))
                t = Tournament()
                t.id = x['BaseCompetitionIndividuelle']['@ID']
                t.season = x['BaseCompetitionIndividuelle']['@Annee']
                t.weapon = x['BaseCompetitionIndividuelle']['@Arme']
                t.gender = x['BaseCompetitionIndividuelle']['@Sexe']
                t.date = datetime.strptime(x['BaseCompetitionIndividuelle']['@Date'], '%d.%m.%Y')
                t.title = x['BaseCompetitionIndividuelle']['@TitreCourt']
                t.title_long = x['BaseCompetitionIndividuelle']['@TitreLong']
                for f in x['BaseCompetitionIndividuelle']['Tireurs']['Tireur']:
                    if type(f) is OrderedDict:
                        fencer = Fencer()
                        fencer.id = f['@ID']
                        fencer.gender = f['@Sexe']
                        fencer.hand = f['@Lateralite']
                        fencer.association = f['@Club']
                        fencer.league = f['@Ligue']
                        fencer.nation = f['@Nation']
                        fencer.name = f['@Prenom']
                        fencer.surname = str(f['@Nom']).lower().capitalize()
                        fencer.birthday = datetime.strptime(f['@DateNaissance'], "%d.%m.%Y")
                        fencer.license = f['@Licence']
                        fencer.paid = f['@paid']
                        fencer.status = f['@Statut']
                        try:
                            fencer.image = Image.open(self.file.open('pictures/F{}.jpg'.format(fencer.id)))
                        except (IOError, KeyError):
                            pass
                        self.fencers.append(fencer)
                        t.fencer.append(fencer)
                self.tournaments.append(t)
        self.fencers = set(self.fencers)
        return {'fencers': self.fencers, 'tournaments': self.tournaments}