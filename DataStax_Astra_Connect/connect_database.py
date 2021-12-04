from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv
from Logging_Layer import logger
import pandas as pd
import os 
from datetime import datetime

class Cassandra:
    def __init__(self, file_object):
        self.file_object = file_object
        self.log_writer = logger.app_logger()
        self.cluster = None
        self.session = None
       
    def connect_datastax(self, keyspace):
        try:
            self.log_writer.log(self.file_object, 'Start of DataStax Connection!!')
 
            load_dotenv()
            username = os.getenv('ASTRA_USER')
            password = os.getenv('ASTRA_PASS')

            cloud_config = {
                'secure_connect_bundle': os.path.join(os.getcwd(),"DataStax_Astra_Connect", "secure-connect-mice.zip")
            }
            auth_provider = PlainTextAuthProvider(username, password)

            self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            self.session = self.cluster.connect()

            self.session.set_keyspace(keyspace)
            print('keyspace set')
            self.log_writer.log(self.file_object, '{}  <-- keyspace set'.format(keyspace))
        
        except Exception as e:
            self.log_writer.log(self.file_object, str(e))
            raise e

    def fetch_data(self):
        try:
            self.log_writer.log(self.file_object, "Entered in fetch_tables method")
            self.session.row_factory = dict_factory

            for i in [1,2]:
                rows = list(self.session.execute("SELECT * FROM table{}".format(i)))
                
                if i==1:
                    df1 = pd.DataFrame(rows)
                elif i==2:
                    df2 = pd.DataFrame(rows)

            self.session.shutdown()
            self.cluster.shutdown()

            self.log_writer.log(self.file_object, 'Exiting fetch_data method after returning data\
                                                 in dataframe and closing open connections')
        
            return pd.merge(df1, df2, how='outer', on='MouseID')

        except Exception as e:
            self.log_writer.log(self.file_object, str(e))
            raise e


    def data_to_excel(self, data, path):
        try:
            self.log_writer.log(self.file_object, "Entered in data_to_excel method")
           
            now = datetime.now()
            dt_string = now.strftime("%d%m%Y_%H%M%S")

            name = 'mice_protein_' + dt_string + '.xls'
                        
            for f in os.listdir(path):
                os.remove(os.path.join(path, f))
            
            if path.split("\\")[-1] == "Prediction_Batch_Files":
                data.drop("class", axis=1, inplace=True)
                
            full_path = os.path.join(path, name)

            data.to_excel(full_path, index=False, header=True)

            self.log_writer.log(self.file_object, "File Created Successfully!!!. Exiting data_to_excel method")

        
        except Exception as e:
            self.log_writer.log(self.file_object, str(e))
            raise e

    
              
