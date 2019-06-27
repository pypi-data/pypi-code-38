from stackapi import StackAPI
import pandas as pd
import sys
def search(a):
    tb = sys.exc_info()[2]
    print(str(a)+" exception at line number: "+str(tb.tb_lineno))
    print("1.Search this error in stackoverflow")
    print("2.I can handle this myself")
    answer=int(input())
    if answer==1:
        SITE=StackAPI("stackoverflow")
        test=SITE.fetch("search",intitle=a,tagged='python',sort='votes')
        test1=pd.DataFrame(test['items'])
        links=test1['link'][0]
        callback(links)
    else:
        exit()
import webbrowser
def callback(url):
    webbrowser.open_new(url)
