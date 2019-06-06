import psycopg2 
import pandas as pd 
import csv 
import os 
import time 
from .logger_setting import logger 


# Defining PostgreSQL Database specific Class to work with

class PostgreSQLConnector: 
    def connect(self, db_name, host, port, user, password, retry_time = 0, buffering = 5):
        attempt = 0
        
        while attempt == 0 or attempt < retry_time:
            try: 
                logger.info("Connecting...") 
                self.connection  = psycopg2.connect(dbname = db_name
                                                    , host = host
                                                    , port = port
                                                    , user = user
                                                    , password = password) 
                logger.info("Connection established.")
                return True 

            except Exception as e:
                attempt += 1
                issue = e 
                message = "Attempt {}. {}. Retrying .....".format(attempt, issue)
                logger.error(message)
                time.sleep(buffering) 
                continue  

            raise RuntimeError("Can not access to PostgreSQL due to: {}".format(issue)) 



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
                cur = self.connection.cursor()
                cur.execute(query) 

                if return_data == True: 
                    data = cur.fetchall()
                    column_names = [desc[0] for desc in cur.description]
                    df = pd.DataFrame(data, columns = column_names) 
                    cur.close() 
                    logger.info("Data is returned")
                    return df 

                else: 
                    cur.close()
                    self.connection.commit()
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
        raise RuntimeError("Cannot query from PostgreSQL server due to: {}".format(issue))
        
        


    def truncate(self, table):
        cur = self.connection.cursor()
        cur.execute("TRUNCATE TABLE %s" % (table)) 



    def uploadCsv(self, filepath, table, fields, truncate = False, remove_file = False): 
        if truncate == True: 
            self.truncate(table)
            logger.info("Table truncated. Start uploading...")

        cur = self.connection.cursor()

        try: 
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = "COPY %s(%s) FROM STDIN WITH ( DELIMITER ',', FORMAT CSV, HEADER, ENCODING 'UTF8', FORCE_NULL(%s))" % (table, fields, fields) 
                cur.copy_expert(sql, f) 
                self.connection.commit()
            if remove_file == True:
                os.remove(filepath) 
            return True

        except Exception as e:
            issue = e 
            raise RuntimeError("Cannot upload to PostgreSQL server due to: {}".format(issue))



    def upsert(self, filepath, table, conflict_resolution = 'new', truncate = False, remove_file = False):
        if truncate == True: 
            self.truncate(table)
            logger.info("Table truncated. Start uploading...")

        reg_sub = lambda x: str(x).replace("'", "''")

        cur = self.connection.cursor()

        try: 
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline() 
                first_line = first_line.replace('"', '')

            
            key_columns = self.run_query("""SELECT               
                                                    pg_attribute.attname, 
                                                    format_type(pg_attribute.atttypid, pg_attribute.atttypmod) 
                                            FROM    pg_index, pg_class, pg_attribute, pg_namespace 
                                            WHERE   1=1
                                                    AND pg_class.oid = '{}'::regclass 
                                                    AND indrelid = pg_class.oid 
                                                    AND nspname = '{}' 
                                                    AND pg_class.relnamespace = pg_namespace.oid 
                                                    AND pg_attribute.attrelid = pg_class.oid 
                                                    AND pg_attribute.attnum = any(pg_index.indkey)
                                                    AND indisprimary""".format(table, table.split(".")[0])
                                        , return_data = True)
            key_columns = list(key_columns["attname"])

            logger.info("Checking key data...")
            for key in key_columns:
                if key not in first_line.split(','): 
                    raise KeyError("Key column {} is not available as in the data. Exiting...")


            with open(filepath, 'r', encoding='utf-8') as f:
                f.readline() 
                ins_data = ''
                for line in f:
                    row = line.replace('"', '')
                    row = row.split(',')
                    ins_data += '(' + ("'{!s}', " * len(row)).format(*list(map(reg_sub, row)))[:-2] + '), '
                ins_data = ins_data.replace('\'None\'', 'NULL').replace(' \'\',', ' NULL,').replace('\'\n\'', 'NULL')[:-2]

            update_condition = ''
            if conflict_resolution == 'new':
                resolution = 'EXCLUDED'
            elif conflict_resolution == 'old':
                resolution = 'tb' 
            
            for column in first_line.split(','):
                if column not in key_columns:
                    update_condition += column + ' = ' + resolution + '.' + column + ','

            basic_insert = "INSERT INTO {}.{} AS tb ({}) VALUES {} ON CONFLICT ({}) DO UPDATE SET {}"
            basic_insert = basic_insert.format( table.split(".")[0],
                                                table.split(".")[1],
                                                first_line,
                                                ins_data,
                                                ','.join(key_columns), 
                                                update_condition 
                                                )
            cur.execute(basic_insert[:-1]) 
            cur.close()
            self.connection.commit()
            logger.info("Data has been UPSERTED.")  
            return True 

        except Exception as e:
            issue = e 
            print(basic_insert[:-1])
            raise RuntimeError("Cannot UPSERT into PostgreSQL server due to: {}".format(issue))



    def disconnect(self):
        state = self.connection.close() 
        logger.info("Connection closed.")
        return state 