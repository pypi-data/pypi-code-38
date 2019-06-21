name = "morph_gen"
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

def finallist(result,stemlist):
        del stemlist[0]
        clist1=stem(result[0])
        if clist1!=None and clist1[0] in mydict:
            del result[0]
            return clist1+result+stemlist
        else:
            return result+stemlist
        
def change(patt):
    if patt=="\u0d41":
        return "ഉ"
    if patt=="\u0d42":
        return "ഊ"
    if patt=="\u0d46":
        return "എ"
    if patt=="\u0d47":
        return "ഏ"
    if patt=="\u0d4a":
        return "ഒ"
    if patt=="\u0d4b":
        return "ഓ"
    if patt=="\u0d3e":
        return "ആ"
    if patt=="\u0d3f":
        return "ഇ"
    else:
        return patt

def excep(x):
    adlist1=["വ്","ത്ത്"]
    for patt in adlist1:
        if x.endswith(patt):
            wx=re.sub(patt+'$',"\u0d02",x)
            if wx in mydict:
                return wx
    return x

def clean(FINAL):
    cleanedList = [x for x in FINAL if str(x) != 'nan']
    k=' '.join(str(x) for x in cleanedList)
    cleanedList = k.split()
    return cleanedList

mydict=li("dictionary.txt")
vedict=li("verb.txt")
mydi=li("suffverb.txt")
mysuffix=li("suffixmorph.txt")
mysuffix1=li("suffixdvithva.txt")
noundict=li("nounsuf.txt")
verdict=li("verbsuf.txt")

ex=pathfile('example.csv')
file=pd.read_csv(ex)
loop = file['letter'].copy()
ch1=pathfile('ch.csv')
file1=pd.read_csv(ch1)
myloop1 = file1['letter'].copy()
ch2=pathfile('change.csv')
filee=pd.read_csv(ch2)
myloop2 = filee['letter'].copy()
      
stop1=["വല്‍","ടി","ര്‍ക്ക്"]
stop2=["നാല്","യ്യ്","ല്ല്","ള്ള്","മ്മ്","\u0d3e"+"യ്","\u0d47"+"യ്"]

def dvithva(x):
    n=len(x)
    mylist = ["ക്ക","പ്പ","ത്ത", "ശ്ശ","ച്ച"]
    
    if any(ext in x for ext in mylist):
        for k in mylist:
            if k in x:
                N=x.index(k)
                if k == x[N:n]:
                    return [x]
                else:
                    if k[2:3]+x[N+3:n] in mysuffix1:
                        Result = [x[0:N],k[2:3]+x[N+3:n]]
                        wordd=fn(x[0:N])
                        if wordd!=None:
                            del Result[0]
                            Result=wordd+Result
                        wordt=sp(Result[0])
                        if wordt!=None:
                            del Result[0]
                            Result=wordt+Result
                        return Result
                    
def sp(x,mylist=None,wolist=None):
    n=len(x)
    wolist=[] if wolist is None else wolist
    mylist=[] if mylist is None else mylist
    flag = False
    x=x.replace(" ","")
    adlist=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
    for pattern in adlist:
        if pattern in x:
            indx=[m.start() for m in re.finditer(pattern,x)]
            N=indx[-1]
            if x[0:N].endswith("മാര്‍"):
                return (mylist)
            if x[0:N].endswith("ല്ല"):
                word1=x[0:N]
            else:
                word1=x[0:N]+"\u0d4d"
            wordlist = stem(word1)
            if wordlist==None:
                wordlist=[word1]
            k=dvithva(wordlist[0])
            if k!=None:
                del wordlist[0]
                wordlist=k+wordlist
            suff=change(pattern)+x[N+1:n]
            if suff in mysuffix:
                flag = True
                mylist.insert(0,suff)
                mylist=wordlist+mylist
                break
                
    if flag:
        word = mylist[0]
        if word in mydict:
            return mylist
        else:
            wor=fn(word)
            if wor!=None:
                del mylist[0]
                mylist=wor+mylist
            wor=ni(mylist[0])
            if wor[0]!=[mylist[0]]:
                del mylist[0]
                mylist=wor+mylist
            wor= last(mylist[0])
            if wor!=None:
                del mylist[0]
                mylist=wor+mylist               
            #print (mylist,"spnotin")
            hj=verb(mylist[0],myloop2,filee,stop1)
            #print (hj,"verbinsp")
            if hj!=[mylist[0]] and hj[0] in mydict:
                del mylist[0]
                mylist=hj+mylist
                return mylist
            elif mylist[0] in mydict:
                return mylist
            del mylist[0] 
            return sp(word,mylist)
    else:
        if x in mydict:
            mylist.insert(0,x)
            return mylist
        else:
            hj=verb(x,myloop2,filee,stop1)
            #print (hj,"verbinsp")
            if hj!=[x] and hj[0] in mydict:
                if mylist!=[]:
                    hj=hj+mylist
                return hj
            st=stem(x)
            if st[0] in mydict:
                st=st+mylist
                return st
            wx=excep(x)
            if wx!=x:
                mylist.insert(0,wx)
                return mylist
            for patt in adlist:
                if x.endswith(patt):
                    x=x[:-1]+"\u0d4d"
                    wo= stem(x)
                    wor1=wo[0]
                    w=sp(wor1)
                    if w!=None:
                        del wo[0]
                        wo=w+wo
                    if wo[0] in mydict:
                        pat=change(patt)
                        wo.append(pat)
                        mylist=wo+mylist
                        return mylist
                    else:
                        wor=re.sub("\u0d4d"+'$',"\u0d41"+"ക",x)
                        if wor in vedict:
                            pat=change(patt)
                            wo.append(pat)
                            mylist=wo+mylist
                            return mylist
                    
def stem(word,mylist=None):
    mylist=[] if mylist is None else mylist
    flag = False
    word=word.replace(" ","")
    stoplist=["പോരെ","ഓയില്‍","കുമാര്‍","മതില്‍","മതില്","വാതില്‍","വാതില്","അബ്ദുള്ള","സുഹൃത്ത്","സമ്പത്ത്","അഭിപ്രായ","നിങ്ങള്‍","ജില്ല","കത്ത്","കരയ്","തിരയ്","പറയ്","അറിയ്","പിരിയ്","നേതാവും","മക്കള്‍","അനുയായി"]
    stop=["ന്നെ","\u0d42"+"ത്ത്","ഴിയ്", "രോ","രും","വില്‍","വില്","ര്‍ത്ത്","ഹാം","ടുവ്","യ്യ്","ന്ന്","ല്ല്","ള്ള്","മ്മ്","\u0d3e"+"ത്ത്","\u0d3f"+"ത്ത്","\u0d41"+"ത്ത്","യിന്‍","\u0d3e"+"വ്","ന്നില്‍","നാല്","ശായി"]
    #print (len(word),";len")
    if word.endswith("\u0d47"+"യ്") and len(word)==4:
        return [word]
    if word in stoplist:
        if mylist==[]:
            return [word]
        else:
            mylist.insert(0,word)
            return mylist
    for patt in stop:
        if word.endswith(patt):
            if mylist==[]:
                return [word]
            else:
                mylist.insert(0,word)
                return mylist
    for pattern in loop:
        if word.endswith(pattern):
            if len(word)>len(pattern)+1:
                n=file.loc[file['letter']==pattern].index[0]
                flag = True
                word1=re.sub(pattern+'$',file.loc[n,'first_change'],word)
                if word1.endswith("ല്ല്"):
                    word1=re.sub("ല്ല്"+'$',"ല്ല",word1)
                second=file.loc[n,'second_change']
                mylist.insert(0,second)
                break
    if flag:
        if word!=word1:
            return stem(word1,mylist)
        else:
            mylist.insert(0,word)
            return mylist
    else:
        if mylist!=None:
            mylist.insert(0,word)
            return mylist
        
def ni(x):
    adlist4=["ല്‍","ര്‍", "ന്‍", "ള്‍","ണ്‍","നെ"]
    for patt in adlist4:
        if x.endswith(patt)==False:
            if patt in x:
                ind=x.index(patt)
                n=len(patt)
                suff= x[ind+n:]
                if suff in mysuffix or suff in mydict:
                    stem5=x[:ind+n]
                    myli=[stem5,suff]
                    stem6=sp(stem5)
                    if stem6!=None and stem6[0] in mydict:
                        del myli[0]
                        myli=stem6+myli
                        return myli
                    else:
                        if myli[0] in mydict:
                            return myli
    return [x]

def fn(word):
    if word in mydict:
        return [word]
    adlist1=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
    for patt in adlist1:
        if patt in word:
            indx=[m.start() for m in re.finditer(patt,word)]
            for N in indx:
                chp=change(patt)+word[N+1:]
                if chp in mysuffix:
                    x=stem(word[:-1]+"\u0d4d")
                    if x[0] in mydict:
                        x.append(chp)
                        return x
                    kd=verb(word[:N]+"\u0d4d",myloop1,file1,stop2)
                    if kd[0] in mydict:
                        kd.append(chp)
                        return kd
                    k=sp(word[:N]+"\u0d4d")
                    if k!=None:
                        k.append(chp)
                        return k
                if (word[N+1:] in mysuffix) or (word[N+1:] in mydict): 
                    sufli=[word[N+1:]]
                    if word[:N+1] in mydict:
                        myli=sufli.insert(0,word[:N+1])
                        return myli
                    else:
                        if word[:N] in mydict:
                            myli=[word[:N],word[N+1:]]
                            return myli
                        elif word[:N]+"\u0d4d" in mydict:
                            return [word[:N]+"\u0d4d",word[N+1:]]
                            
                if word.endswith(patt): 
                    if word[:-1] in mydict:
                        return [word[:-1],change(patt)]
                    elif word[:-1]+"\u0d4d" in mydict:
                        k1=word[:-1]+"\u0d4d"
                        k2=sp(k1)
                        if k2==None:
                            k2=[word[:-1]+"\u0d4d"]
                        k2.append(change(patt))
                        return k2
                    
def verb(word,myloop,file1,stop):
    word=word.replace(" ","")
    for patt in stop:
        if word.endswith(patt):
            return [word]
    for pattern in myloop:
        if word.endswith(pattern):
            n=file1.loc[file1['letter']==pattern].index[0]
            word1=re.sub(pattern+'$',file1.loc[n,'first_change'],word)
            second=file1.loc[n,'suff']
            mylist=[word1,second]
            return mylist
    return [word]

def last(x):
    adlistd=["ത","ല","ന","ച","ണ","യ","ര","ക്ക","ള","ണ്ട","മ","ഞ്ഞ"]
    for patt in adlistd:
        if x.endswith(patt)==False:
            if patt in x:
                indx=[m.start() for m in re.finditer(patt,x)]
                n=len(patt)
                for N in indx:
                    suf="അ"+x[N+n:]
                    sufl=[suf]
                    if (suf in mysuffix) or (suf in mydict):
                        k=sp(x[:N+n]+"\u0d4d")
                    else:
                        stemi=verb(suf,myloop2,filee,stop1)
                        if stemi[0] in mydict:
                            k=sp(x[:N+n]+"\u0d4d")
                            sufl=stemi
                        else:
                            k=None
                    if k!=None and k[0] in mydict:
                        li=k+sufl
                        return li
                    

def morph(word):
    x=re.sub('[0-9]+', '',word)
    remove=str.maketrans('', '', string.punctuation)
    x=x.translate(remove)
    x=x.replace(" ","")
    word=x.replace("ർ","ര്‍").replace("ൾ","ള്‍").replace("ൽ","ല്‍").replace("ൺ","ണ്‍").replace("ൻ","ന്‍").replace("‌","")
    stemlist=stem(word)
    adlist1=["\u0d41","\u0d42","\u0d46","\u0d47","\u0d4a","\u0d4b","\u0d3e","\u0d3f"]
    adlist2=["ല്‍","ര്‍", "ന്‍", "ള്‍","ണ്‍","നെ"]
    adlist3=["ക്ക","പ്പ", "ത്ത", "ശ്ശ","ച്ച"]
    adlistd=["ത","ല","ന","ച","ണ","യ","ര","ക്ക","ള","ണ്ട","മ","ഞ്ഞ"]

    split=[stemlist[0]]
    
    if any(ltr in split[0] for ltr in adlist2):
        stemj=ni(split[0])
        if stemj!=[word]:
            split=stemj
            
    worddv=split[0]

    if any(ltr in worddv for ltr in adlist3):
        splitd=dvithva(worddv)
        #print("3",splitd)
        if splitd!=None:
            split=finallist(splitd,split)

    wordsp=split[0]

    if any(ltr in wordsp for ltr in adlist1):
        splits=sp(wordsp)
        if splits!=None:
            split=finallist(splits,split)
    
    wordfn=split[0]
    
    wordsli=fn(wordfn)
    #print (wordsl,"fn")    
    if wordsli!=None:
        split=finallist(wordsli,split)

    wordlt=split[0]
    
    if any(ltr in wordlt for ltr in adlistd):
            splitlt=last(wordlt)
            if splitlt!=None:
                split=finallist(splitlt,split)
                
    word5=split[0]

    stem2=verb(word5,myloop2,filee,stop1)
    if stem2[0] in vedict:
        split=finallist(stem2,split)
    else:
        stem2=verb(word5,myloop1,file1,stop2)
        if stem2[0] in mydict:
            split=finallist(stem2,split)
            
    if split!=None:
        FINAL=finallist(split,stemlist)
    else:
        FINAL=stemlist

    wordf=FINAL[0]
    worex=excep(wordf)
    if worex!=wordf:
        del FINAL[0]
        FINAL.insert(0,worex)
        
    wordfi=FINAL[0]
    if wordfi.endswith("ക്ക്"):
        wori=re.sub("ക്ക്"+'$',"",wordfi)
        if wori in mydict:
            del FINAL[0]
            FI=[wori,"ക്ക്"]
            FINAL=FI+FINAL

    cleanedList=clean(FINAL)
               
    return cleanedList   