import pandas
import pygsheets

def gs2df(gdrive_creds, book, tab):
    
    #get the sheet from google sheets
    gc = pygsheets.authorize(service_file = gdrive_creds)
    wks = gc.open(book).worksheet_by_title(tab)
    
    #convert the sheet to dataframe
    df = pd.DataFrame(wks.get_all_records())

    return df

def df2gs(df, gdrive_creds, book, tab):
    gc = pygsheets.authorize(service_file = gdrive_creds)
    wks = gc.open(book).add_worksheet(tab)
    wks.set_dataframe(df,(1,1))

def add(x, y):
    return x+y
    
def main():
    pass

if __name__ == '__main__':
    main()