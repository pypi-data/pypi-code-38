from google.cloud import firestore
import json
import csv

class db:
	def __init__(self):
		self.db = firestore.Client()

	def list(self):
		return [i.id for i in self.db.collections()]
	
	def backup(self, *Collections, All=False):
		if All: 
			Collections = self.list()
		for name in Collections:
			Col = self.db.collection(name)
			L = [(i.id,i.to_dict()) for i in Col.get()]
			json.dump(L, open(f'{name}.json','w'))
			print(f'{name}.json is created' )
			
	def restore(self, BackupFile):
		L = json.load(open(BackupFile))
		Col = self.db.collection(BackupFile.replace('.json',''))
		for i in range(len(L)):
			Col.document(L[i][0]).set(L[i][1])

	def csv2collection(self, CSVFile, name=''):
		rows = csv.reader(open(CSVFile))
		L = [r for r in rows]
		Header = L.pop(0)
		L.sort()
		DList = []
		for n in range(len(L)):
			d = {}
			for i in range(len(Header)):
				d.update({Header[i]: L[n][i]})
			DList.append(d)
		Col = self.db.collection(CSVFile.replace('.csv',''))
		for i in range(len(DList)):
			if name is '':
				Col.document(str(i+1)).set(DList[i])
			else:
				Col.document(DList[i][name]).set(DList[i])
		print(f'{CSVFile} is converted to Collection')
