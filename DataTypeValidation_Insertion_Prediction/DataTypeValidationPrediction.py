import shutil
import sqlite3
# from datetime import datetime
from Logging_Layer import logger
from os import listdir
import os
import csv

class dBOperation:

    def __init__(self):
        self.path = 'Prediction_Database/'
        self.badFilePath = "Prediction_Raw_Files_Validated/Bad_Raw"
        self.goodFilePath = "Prediction_Raw_Files_Validated/Good_Raw"
        self.logger = logger.app_logger()

    def dataBaseConnection(self, DatabaseName):

        try:
            conn = sqlite3.connect(self.path + DatabaseName + '.db')

            file = open("Prediction_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Opened %s database successfully" % DatabaseName)
            file.close()
            return conn
        except ConnectionError:
            print("CONNECTION ERROR")
            conn.close()
            
            file = open("Prediction_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Error while connecting to database: %s" % ConnectionError)
            file.close()
            raise ConnectionError
        

    def createTableDb(self, column_names):

        try:
            files_in_directory = os.listdir("Prediction_Database")

            for file in files_in_directory:
                path_to_file = os.path.join("Prediction_Database", file)
                os.remove(path_to_file)

            only_files = [f for f in listdir(self.goodFilePath)]
            file = open("Training_Logs/DbTableCreateLog.txt", 'a+')

            for filename in only_files: 
                tablename = "Table_" + str(filename.split(".")[0] )
                conn = self.dataBaseConnection(tablename)
                c = conn.cursor()
                c.execute('DROP TABLE IF EXISTS {table};'.format(table = tablename))
                # c.execute("SELECT count(name)  FROM sqlite_master WHERE type = 'table' AND name = 'Good_Raw_Data'")
                # if c.fetchone()[0] == 1:
                #     conn.close()
                #     file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                #     self.logger.log(file, "Tables created successfully!!")
                #
                #     self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                #     file.close()
                #
                # else:

                for name, type_ in column_names.items():
                    try:
                        conn.execute('ALTER TABLE {table} ADD COLUMN {column_name} {dataType};'
                                    .format(table=tablename, column_name=name, dataType=type_))

                    except:
                        conn.execute('CREATE TABLE IF NOT EXISTS {table} ({column_name} {dataType} UNIQUE);'.format(
                                table=tablename, column_name=name, dataType=type_))
                        continue
                
                self.logger.log(file, "Table %s created successfully!!" % tablename)

                conn.close()
            # file.close()

            # file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Closed database successfully")
            file.close()

        except Exception as e:
            file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
            self.logger.log(file, "Error while creating table: %s " % e)
            file.close()
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Closed database successfully")
            file.close()
            raise e

    def insertIntoTableGoodData(self):

        
        goodFilePath = self.goodFilePath
        badFilePath = self.badFilePath
        only_files = [f for f in listdir(goodFilePath)]
        log_file = open("Prediction_Logs/DbInsertLog.txt", 'a+')

        for file in only_files:
            try:
                conn = self.dataBaseConnection("Table_" + str(file).split(".")[0])
                with open(goodFilePath + '/' + file, "r") as f:
                    # next(f)
                    reader = csv.reader(f, delimiter="\n")
                    for line in enumerate(reader):
                        entries = tuple(line[1][0].split(sep=','))
                        try:
                            conn.execute('INSERT OR REPLACE INTO {table} values {values}'.format(table="Table_"+ str(file.split(".")[0]),
                                                         values=entries))
                            conn.commit()
                        except Exception as e:
                            raise e
                    self.logger.log(log_file, " %s: File loaded successfully!!" % file)
                conn.close()
                
            except Exception as e:

                conn.rollback()
                self.logger.log(log_file, "Error while creating table: %s " % e)
                shutil.move(goodFilePath + '/' + file, badFilePath)
                self.logger.log(log_file, "File Moved Successfully %s" % file)
                log_file.close()
                conn.close()
                raise e

        log_file.close()

    def selectingDatafromtableintocsv(self):

        fileFromDb = 'Prediction_FileFromDB/'
        log_file = open("Prediction_Logs/ExportToCsv.txt", 'a+')
        only_files = [f for f in listdir("Prediction_Database")]
        try:
            for file in only_files:
            # for filename in only_files: 
                tablename = str(file.split(".")[0] )
                conn = self.dataBaseConnection(tablename)
                # c = conn.cursor()
                # conn = self.dataBaseConnection(Database)
                sqlSelect = "SELECT *  FROM {table}".format(table= str(file.split(".")[0]))
                cursor = conn.cursor()
                cursor.execute(sqlSelect)

                results = cursor.fetchall()
                # Get the headers of the csv file
                # headers = [i[0] for i in cursor.description]

                # Make the CSV output directory
                if not os.path.isdir(fileFromDb):
                    os.makedirs(fileFromDb)

                # Open CSV file for writing.
                fileName = str(file.split(".")[0]) + '.csv'
                
                with open(os.path.join(fileFromDb + fileName), 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=',',
                                    lineterminator='\r\n', quoting=csv.QUOTE_ALL, escapechar='\\')
                    csvwriter.writerows(results)

                self.logger.log(log_file, "File exported successfully!!!")
                conn.close()

        except Exception as e:
            self.logger.log(log_file, "Exception in selectingDatafromtableintocsv method. File exporting failed. Error : %s" % e)
            raise e
