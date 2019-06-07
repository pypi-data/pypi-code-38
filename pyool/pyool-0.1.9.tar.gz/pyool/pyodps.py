import csv 
from datetime import datetime
from odps import ODPS 
import time 
import uuid 
import os 
from .logger_setting import logger  


# Defining ODPS specific class to work with 

class OdpsConnector: 

    def connect(self, accessId, accessKey, project, endPoint, tunnelEndPoint, retry_time = 0, buffering = 5):
        attempt = 0

        while attempt == 0 or attempt < retry_time:
            try: 
                logger.info("Connecting...") 

                self.connection = ODPS(
                    access_id = accessId
                    , secret_access_key = accessKey
                    , project = project
                    , endpoint = endPoint 
                    ,tunnel_endpoint = tunnelEndPoint
                ) 
                logger.info("Connection established.")
                return True 

            except Exception as e:
                attempt += 1
                issue = e 
                message = "Attempt {}. {}. Retrying .....".format(attempt, issue)
                logger.error(message)  
                time.sleep(buffering) 
                continue  

        raise RuntimeError("Can not access to ODPS due to {}".format(issue)) 



    def read_sql(self, file_path):
        with open(file_path, "r", encoding = "utf-8") as file:
            query  = file.read()

        return query 
    


    def extract_header(self, csv_file_path): 
        with open(csv_file_path, "r", newline = "") as file:
            reader = csv.reader(file)
            header = ",".join(next(reader))

        return header 



    def run_query(self, query, return_data = False, retry_time = 0, buffering = 5):  
        
        attempt = 0

        while attempt == 0 or attempt < retry_time:
            try:
                logger.info("Querying.....") 

                with self.connection.execute_sql(query, None, 1, hints = {"odps.sql.submit.mode" : "script"}).open_reader() as reader:
                    logger.info("Query is finished")

                    if return_data == True: 
                        return reader.to_pandas()  
                    else: 
                        return reader 
            except Exception as e:
                attempt += 1
                issue = e 
                message = "Attempt {}. {}. Retrying .....".format(attempt, issue)
                logger.error(message)  
                time.sleep(buffering) 
                continue  
        
        raise RuntimeError("Cannot query from ODPS due to: {}".format(issue)) 



    def dump_to_csv(self, query, storage_path, filename = None, retry_time = 0, buffering = 5): 
        if not filename:
            filename = str(uuid.uuid4())

        filename = filename + ".csv"

        filepath = os.path.join(storage_path, filename)

        reader = self.run_query(query, retry_time = retry_time, buffering = buffering)
        logger.info("Done dumping to csv file {}".format(filename))
        with open(filepath, "w", encoding ="utf-8") as file:
            writer = csv.writer(file, delimiter = ",", quoting = csv.QUOTE_NONNUMERIC
                                , lineterminator = "\n")
            
            writer.writerow(reader._schema.names)

            for record in reader: 
                writer.writerow(record[0:])
        
        return filepath
            











