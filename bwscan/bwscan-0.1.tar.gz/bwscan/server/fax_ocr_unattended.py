# this is a long running script. Nothing too fancy.
from O365 import Account, FileSystemTokenBackend
from time import sleep
from datetime import datetime
from os.path import isfile
from os import remove as delfile
from yaml import dump as ydump
from yaml import load as yload
#from yaml import FullLoader
from PIL import Image 
import pytesseract 
from pdf2image import convert_from_path 
import signal
from sys import exit as sys_exit
from sys import argv
from tqdm import tqdm
from argparse import ArgumentParser

def getTime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def processPDF(infile):
    text = None
    PDF_file = infile

    ''' 
    Part #1 : Converting PDF to images 
    '''

    # Store all the pages of the PDF in a variable 
    pages = convert_from_path(PDF_file, 500) 
    # Counter to store images of each page of PDF to image 
    image_counter = 1
    # Iterate through all the pages stored above 
    for page in pages: 
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG') 
        image_counter = image_counter + 1

    ''' 
    Part #2 - Recognizing text from the images using OCR 
    '''
    # Variable to get count of total number of pages 
    filelimit = image_counter-1
    # Iterate from 1 to total number of pages 
    for i in range(1, filelimit + 1): 
        filename = "page_"+str(i)+".jpg"
        text = str(((pytesseract.image_to_string(Image.open(filename))))) 
    return text

def getMessagesFromMailbox(cfg):
    credentials = (cfg['outlook'].get("client_id","NONE"),cfg['outlook'].get("client_secret","NONE"))
    if credentials[0] == "NONE" or credentials[1] == "NONE": raise Exception("could not find client_id or client_secret in configuration")
    token_backend = FileSystemTokenBackend(token_path=cfg['control'].get("execution_directory","/tmp"), token_filename='my_token.txt')
    account = Account(credentials, token_backend=token_backend)
    scopes = ['https://graph.microsoft.com/Mail.ReadWrite', 'https://graph.microsoft.com/Mail.Send']
    account = Account(credentials)
    if not account.is_authenticated:  # will check if there is a token and has not expired
        # ask for a login
        account.authenticate(scopes=scopes)
    mailbox = account.mailbox()
    query1 = mailbox.new_query().on_attribute("from").contains("scanner@bestwestern.se")
    query2 = mailbox.new_query().on_attribute("isRead").equals(False)
    query = query1 and query2
    messages = mailbox.get_messages(query=query,limit=int(cfg['outlook'].get("msg_limit","50")))
    return messages

def getHotelLibrary(cfg):
    libfile = "hotel_library.yaml"
    hotel_library = {}
    if isfile(libfile):
        hotel_library = yload(open(libfile,"rb"))#,Loader=FullLoader)
        return hotel_library
    # some exercises with the lime API
    import pandas as pd
    from requests import get
    api_key=cfg['lime'].get("api_key","NONE")
    if api_key == "NONE": 
        raise Exception("api_key missing in configuration")
    headers={'x-api-key': api_key}
    base_url=cfg['lime'].get("base_url","NONE")
    if base_url == "NONE": raise Exception("base_url missing in configuration file")
    from tqdm import tqdm
    for i in tqdm(range(1000),desc='looking up hotels and assembling lookup table for hotels -- please hold, this may take a bit of time.'):
        r = get("{url}/api/v1/limeobject/hotels/{hotel_id}/".format(url=base_url,hotel_id=i+1000),headers=headers)
        if r.ok: 
            data = r.json()
            if not bool(data.get("memberhotel","False")): continue
            hotel_library[data.get("propertynumber","")] = data.get("email","")
    with open("hotel_library.yaml","wb") as f:
        f.write(ydump(hotel_library))
    return hotel_library

def run_processing(cfg):
    print("{time}: running message processing".format(time=getTime()))
    hotels = getHotelLibrary(cfg)
    messages = getMessagesFromMailbox(cfg)
    for m in messages: #tqdm(messages, total=int(cfg['outlook'].get("msg_limit",50)), desc="processing mailbox messages"):
        processed = False
        if m.is_read: continue
        if m.has_attachments:
            rc = m.attachments.download_attachments()
            if not rc: 
                print("could not download attachments from server {msg}".format(msg=str(m)))
                continue
            att = m.attachments[0]
            filename = att.name
            # if attachment is pdf and can be saved to current directory, proceed
            if len(att.name.split(".pdf")) > 1 and att.save():
                text = processPDF(filename)
                if text is None: 
                    print("message could not be processed {msg}".format(msg=str(m)))
                    delfile(filename)
                    continue
                to_email = "distribution@bestwestern.se"
                # look up text to see if we can find the property ID
                for prop,email in hotels.items():
                    if processed: break
                    for line in text.split("\n"):
                        if "P{prop}".format(prop=prop) in line: 
                            to_email = email
                            processed = True
                            break
                if processed:
                    # now - if all of this is working, let's forward the email.
                    try:
                        new_message = m.forward()
                        #print(prop, to_email,new_message)
                        new_message.to.add(to_email)
                        rc = new_message.send()
                        if rc: 
                            delfile(filename)
                            m.mark_as_read()
                        else: raise Exception("failed sending forwarded email.")
                    except Exception as err:
                        print("encountered an error with {msg}, error message follows after new line \n{err}".format(msg=str(m),err=str(err)))
                        processed = False
                        continue
                else:
                    print("could not identify property ID in decoded message {msg}".format(msg=str(m)))
                pass
            else:
                print("message contained attachment, but either no pdf or the attachment could not be saved: {msg}".format(msg=str(m)))


def main(args=None):
    parser = ArgumentParser(usage="Usage: %(prog)s [options]", description="initialize unattended fax OCR")
    parser.add_argument("-f", "--file", dest="file", type=str, default=None, required=True,
                        help='use this flag if you plan to provide a file')
    opts = parser.parse_args(args)
    if opts.file is not None:
        cfg = yload(open(opts.file))#,Loader=FullLoader)
        sleeptime = int(cfg['control'].get("sleep_time",1800))
        print("{time}: starting our run".format(time=getTime()))
        while True:
            run_processing(cfg)
            print("{time}: finished cycle, will now sleep for {i} seconds".format(time=getTime(),i=sleeptime))
            sleep(sleeptime)
    return
 
if __name__ == "__main__":
    main()


#def exit_gracefully(signum, frame):
#    # restore the original signal handler as otherwise evil things will happen
#    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
#    signal.signal(signal.SIGINT, original_sigint)#
#
#    try:
#        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
# #            sys_exit(1)

#     except KeyboardInterrupt:
#         print("Ok ok, quitting")
#         sys_exit(1)

#     # restore the exit gracefully handler here    
#     signal.signal(signal.SIGINT, exit_gracefully)

# if __name__ == '__main__':
#     cfg_file = argv[1]
#     cfg = yload(open(cfg_file))#,Loader=FullLoader)
#     # store the original SIGINT handler
#     original_sigint = signal.getsignal(signal.SIGINT)
#     signal.signal(signal.SIGINT, exit_gracefully)
#     main(cfg)

