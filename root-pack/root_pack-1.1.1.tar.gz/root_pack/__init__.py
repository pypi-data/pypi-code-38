name = "root_pack"
import pandas as pd
import re
import string
import os

def pathfile(file):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, file)
    return my_file

def li(file):
    my_file = pathfile(file)
    dictfile=open(my_file,"r")
    dictlines=dictfile.read()
    mydict=[]
    mydict=dictlines.split()
    return mydict

mydict=li("dictionary.txt")
mysuffix=li("suffixmorph.txt")
vedict=li("verb.txt")
ex=pathfile('example.csv')
file=pd.read_csv(ex)
loop = file['letter'].copy()
ch1=pathfile('ch.csv')
file1=pd.read_csv(ch1)
myloop = file1['letter'].copy()
ch2=pathfile('change.csv')
filee=pd.read_csv(ch2)
myloop2 = filee['letter'].copy()
stop1=["വല്‍","ടി","ര്‍ക്ക്"]
stop2=["നാല്","യ്യ്","ല്ല്","ള്ള്","മ്മ്","\u0d3e"+"യ്","\u0d47"+"യ്"] 

def dvithva(x):
	n=len(x)
	mysuffix1=li("suffixdvithva.txt")
	mylist = []
	mylist = ["ക്ക","പ്പ","ത്ത", "ശ്ശ","ച്ച"]
	if any(dl in x for dl in mylist):
		for k in mylist:
			if k in x:
				lis=[m.start() for m in re.finditer(k,x)]
				for N in lis: 
					if k == x[N:n]:
						return x
					else:
						if k[2:3]+x[N+3:n] in mysuffix1:
							wordd=fn(x[0:N])
							if wordd==None:
								wordd=x[0:N]
							wordt=sp(wordd)
							if wordt==None:
								wordt=wordd
							if wordt in mydict:
								return wordt

def stem(word):
	flag = False
	word=word.replace(" ","")
	stoplist=["കടത്ത്","ഫോട്ടോ","ആദായ","ഓയില്‍","നടത്ത്","പഞ്ചായത്ത്","മതില്‍","വാതില്‍","അബ്ദുള്ള","സുഹൃത്ത്","അഭിപ്രായ","നിങ്ങള്‍","ജില്ല","കത്ത്","കരയ്","തിരയ്","പറയ്","അറിയ്","പിരിയ്","നേതാവും","മക്കള്‍","അനുയായി"]
	stop=["റയ്","പ്പിക്ക്","ന്നെ","കുമാര്‍","\u0d42"+"ത്ത്","യ്യും","ഴിയ്","രും","സമ്പത്ത്","തൊഴില്‍","രോ","താവും","വില്‍","ര്‍ത്ത്","ഹാം","ടുവ്","യ്യ്","ന്ന്","ല്ല്","ള്ള്","ണ്ണ്","\u0d3e"+"ത്ത്","\u0d3f"+"ത്ത്","\u0d41"+"ത്ത്","യിന്‍","\u0d3e"+"വ്","ന്നില്‍","നാല്","ശായി"]
	#print (len(word),";len")
	adlist=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
	if word.endswith("\u0d47"+"യ്") and len(word)==4:
		return word 
	if word in stoplist:
		return word
	for patt in stop:
		if word.endswith(patt):
			return word 
	for pattern in loop:
		if word.endswith(pattern):
			if len(word)>len(pattern)+1:
				n=file.loc[file['letter']==pattern].index[0]
				flag = True
				word1=re.sub(pattern+'$',file.loc[n,'first_change'],word) 
				break
	if flag:
		if word!=word1:
			return stem(word1)
	else:
		return word

def verb(word,myloop,file1,stop):
	word=word.replace(" ","")
	for patt in stop:
		if word.endswith(patt):
			return word
	for pattern in myloop:
		if word.endswith(pattern):
				n=file1.loc[file1['letter']==pattern].index[0]
				word1=re.sub(pattern+'$',file1.loc[n,'first_change'],word)
				if word1 in vedict:
					return word1
	return word

def change(patt):
	if patt=="\u0d41":
		return "ഉ"
	elif patt=="\u0d42":
		return "ഊ"
	elif patt=="\u0d46":
		return "എ"
	elif patt=="\u0d47":
		return "ഏ"
	elif patt=="\u0d4a":
		return "ഒ"
	elif patt=="\u0d4b":
		return "ഓ"
	elif patt=="\u0d3e":
		return "ആ"
	elif patt=="\u0d3f":
		return "ഇ"
	else:
		return patt

def spst(word):
	x= stem(word)
	if x==None:
		x=word
	d= dvithva(x)
	if d!=None:
		x=d
	return x     
    
def sp(x):
	n=len(x)
	flag = False
	x=x.replace(" ","")
	stoplist=["മനസ്സിലാക്ക്"]
	if x in stoplist:
		return x
	adlist=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
	x=spst(x)
	for pattern in adlist:
		if pattern in x:
			indx=[m.start() for m in re.finditer(pattern,x)]
			N=indx[-1]
			if x[0:N].endswith("ല്ല") or x[0:N].endswith("ണ്ട"):
				word1=x[0:N]
			else:
				word1=x[0:N]+"\u0d4d"
			word1=spst(word1)
			suff=change(pattern)+x[N+1:n]
			if suff in mysuffix:
				flag = True
				break
	if flag:
		word = word1
		word=word.replace(" ","")
		if word in mydict:
			return word
		else:
			wor=fn(word)
			if wor!=None:
				word=wor
			wor=dvithva(word)
			if wor!=None:
				word=wor
			wor=ni(word)
			if wor!=None:
				word=wor
			wor= last(word)
			if wor!=None:
				word=wor   
			hj=verb(word,myloop2,filee,stop1)
			if hj in mydict:
				return hj
			if word in mydict:
				return word                
			return sp(word)

	else:
		if x in mydict:
			return x
		else:
			if x.endswith("വ്"):
				x=x.replace("വ്"+'$',"\u0d02")
				if x in mydict:
					return x
			for patt in adlist:
				if x.endswith(patt):
					x=x[:-1]+"\u0d4d"
					wo= stem(x)
					wor1=wo[0]
					w=sp(wor1)
					if w!=None:
						wo=w
					if wo in mydict:
						return wo

def ni(x):
	adlist4=["ല്‍","ര്‍", "ന്‍", "ള്‍","ണ്‍","നെ"]
	for patt in adlist4:
		if x.endswith(patt)==False:
			if patt in x:
				ind=x.index(patt)
				n=len(patt)
				if x[ind+n:] in mysuffix or x[ind+n:] in mydict:
					stem5=x[:ind+n]
					stem6=spst(stem5)
					if stem6!=None and stem6 in mydict:
						x=stem6
					else:
						stem7=sp(stem6)
						if stem7!=None:
							x=stem7
	return x 

def last(x):
	adlistd=["ത","ല","ന","ച","ണ","യ","ര","ക്ക","ള"]
	for patt in adlistd:
		if x.endswith(patt)==False:
			if patt in x:
				indx=[m.start() for m in re.finditer(patt,x)]
				n=len(patt)
				for N in indx:
					suf="അ"+x[N+n:]
					if (suf in mysuffix) or (suf in mydict):
						k=sp(x[:N+n]+"\u0d4d")
						if k in mydict:
							return k


def fn(word):
	if word in mydict:
		return word
	adlist1=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
	for patt in adlist1:
		if patt in word:
			indx=[m.start() for m in re.finditer(patt,word)]
			for N in indx:             
				if change(patt)+word[N+1:] in mysuffix:
					x=verb(word[:-1]+"\u0d4d",myloop,file1,stop2)
					if x in mydict:
						return x 
					k=sp(word[:N]+"\u0d4d")
					if k in mydict:
						return k                
				if (word[N+1:] in mysuffix) or (word[N+1:] in mydict):
					if word[:N+1] in mydict:
						return word[:N+1]
					else:
						if word[:N] in mydict:
							return word[:N]
						k=sp(word[:N]+"\u0d4d")
						if k==None:
							k=word[:N]+"\u0d4d"
						k=verb(k,myloop,file1,stop2)                     
						if k in mydict:
							return k
				if word.endswith(patt): 
					if word[:-1] in mydict:
						return word[:-1]
					elif word[:-1]+"\u0d4d" in mydict:
						k1=word[:-1]+"\u0d4d"
						k2=sp(k1)
						ki=verb(k1,myloop,file1,stop2)
						return ki 
                    
def root(word):
	x=re.sub('[0-9]+', '',word)
	remove=str.maketrans('', '', string.punctuation)
	x=x.translate(remove)
	x=x.replace("ർ","ര്‍").replace("ൾ","ള്‍").replace("ൽ","ല്‍").replace("ൺ","ണ്‍").replace("ൻ","ന്‍").replace("‌","")
	steml=stem(x)
	if steml==None:
		steml=x
	adlist1=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
	adlist2=["ല്‍","ര്‍", "ന്‍", "ള്‍","ണ്‍","നെ"]
	adlist3=["ക്ക","പ്പ", "ത്ത", "ശ്ശ","ച്ച"]
	adlistd=["ത","ല","ന","ച","ണ","യ","ര","ക്ക","ള"]

            
	if any(ltr in steml for ltr in adlist2):
		stemj=ni(steml)
		if stemj!=None:
			steml=stemj
    
	if any(ltr in steml for ltr in adlist3):
		stem1=dvithva(steml)
		if stem1!=None:
			steml=stem1

	if any(ltr in steml for ltr in adlist1):
		stem1=sp(steml)
		if stem1!=None:
			steml=stem1

	words=fn(steml)    
	if words!=None:
		steml=words
                        
    
	if any(ltr in steml for ltr in adlistd):
		stemdi=last(steml)
		if stemdi!=None:
			steml=stemdi

	stem2=verb(steml,myloop2,filee,stop1)
	if stem2!=steml and stem2!=None:
		return stem2
	else:
		stem2=verb(steml,myloop,file1,stop2)
		if stem2!=None and stem2 in mydict:
			return stem2

	return (steml)