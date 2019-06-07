from .logger_setting import logger 
from O365 import Account, MSGraphProtocol, oauth_authentication_flow
import os


class OneDriver():

    def self_authenticate(self, client_id, client_secret):
        try: 
            oauth_authentication_flow(client_id, client_secret, scopes = ['onedrive'])
            logger.info("Self Authentication to get Token is executed. There will be a .txt file with token information can be found in the same folder of the .py file.")
            return True 
        except Exception as e: 
            logger.error(e)  
            raise RuntimeError("Cannot access to OneDrive due to: {}".format(e)) 



    def connect(self, client_id, client_secret, user):
        credentials = (client_id, client_secret)

        try: 
            account = Account(credentials, main_resource = user)
            return account  
        except Exception as e: 
            logger.error(e)  
            raise RuntimeError("Cannot access to OneDrive due to: {}".format(e)) 



    def locate_root_folder(self, account): 
        root_folder = account.storage().get_default_drive().get_root_folder()
        return root_folder 

    
    
    def upload(self, folder, file_path_list):
        item_id_list= []
        
        for file_path in file_path_list:
            try: 
                item_id = folder.upload_file(item = file_path)
                item_id_list.append(item_id)
                logger.info("{} uploaded successful with item_id = {}".format(os.path.basename(file_path), item_id))

            except Exception as e: 
                logger.error(e)  
                continue 


        



