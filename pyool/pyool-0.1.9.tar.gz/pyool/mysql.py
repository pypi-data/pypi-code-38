import mysql.connector 
import pandas as pd 
import os 
import time 
import csv 
from .logger_setting import logger  


# Defining MySQL specific class to work with 

class MySQLConnector: 

    def connect(self, db_name, host, port, user, password, retry_time = 0, buffering = 5): 
        attempt = 0

        while attempt == 0 or attempt < retry_time:
            try: 
                logger.info("Connecting...") 
                self.connection = mysql.connector.connect(
                                                            database = db_name,
                                                            host = host,
                                                            port = port,
                                                            user = user,
                                                            passwd = password
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

        raise RuntimeError("Can not access to MySQL server due to: {}".format(issue)) 

    
    def read_sql(self, file_path):
        with open(file_path, "r", encoding = "utf-8") as file:
            query = file.read()

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
                logger.info("Start querying .....")
                cur = self.connection.cursor()
                cur.execute(query)

                if return_data == True:
                    column_names = cur.column_names
                    data = cur.fetchall()
                    df = pd.DataFrame(data, columns = column_names) 
                    cur.close()
                    logger.info("Data is returned")
                    return df 
                else: 
                    cur.close()
                    logger.info("Query is executed") 
                    return True 
            
            except Exception as e: 
                attempt += 1
                issue = e 
                message = "Attempt {}. {}. Retrying .....".format(attempt, issue)
                logger.error(message)
                time.sleep(buffering) 
                continue  

        self.connection.rollback()
        raise RuntimeError("Cannot query from MySQL server due to: {}".format(issue))
                 

    def disconnect(self):
        self.connection.close() 
