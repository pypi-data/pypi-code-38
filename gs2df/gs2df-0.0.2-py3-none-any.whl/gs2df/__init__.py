import pandas as pd
import pygsheets

def gs2df(oauth_creds, book):
    
    #get sheets from google sheets and convert them into df
    gc = pygsheets.authorize(client_secret = oauth_creds)
    wks = gc.open(book)
    
    df_list = []
    for i in wks:
        df_list.append(pd.DataFrame(i.get_all_records()))

    return df_list

def df2gs(df, oauth_creds, book, tab):
    gc = pygsheets.authorize(client_secret = oauth_creds)
    wks = gc.open(book).add_worksheet(tab)
    wks.set_dataframe(df,(1,1))
    
def main():
    pass

if __name__ == '__main__':
    main()