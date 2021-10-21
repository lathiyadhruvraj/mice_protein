import shutil
import sqlite3
from os import listdir
import os
import csv
from Logging_Layer.logger import app_logger


class dBOperation:

    def __init__(self):
        self.path = 'Training_Database/'
        self.badFilePath = "Training_Raw_files_validated/Bad_Raw"
        self.goodFilePath = "Training_Raw_files_validated/Good_Raw"
        self.logger = app_logger()

    def dataBaseConnection(self, DatabaseName):

        try:
            conn = sqlite3.connect(self.path + DatabaseName + '.db')

            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Opened %s database successfully" % DatabaseName)
            file.close()
        except ConnectionError:
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Error while connecting to database: %s" % ConnectionError)
            file.close()
            raise ConnectionError
        return conn

    def createTableDb(self, DatabaseName, column_names):

        try:

            conn = self.dataBaseConnection(DatabaseName)
            c = conn.cursor()
            c.execute("SELECT count(name)  FROM sqlite_master WHERE type = 'table' AND name = 'Good_Raw_Data'")
            if c.fetchone()[0] == 1:
                conn.close()
                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")

                self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                file.close()

            else:

                for name, type_ in column_names.items():

                    # in try block we check if the table exists, if yes then add columns to the table
                    # else in catch block we will create the table
                    try:
                        conn.execute(
                            'ALTER TABLE Good_Raw_Data ADD COLUMN {column_name} {dataType};'.format(column_name=name,
                                                                                                    dataType=type_))
                    except:
                        conn.execute('CREATE TABLE IF NOT EXISTS Good_Raw_Data'
                                     ' ({column_name} {dataType} UNIQUE);'.format(column_name=name, dataType=type_))
                        continue

                conn.close()

                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()

                file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                file.close()

        except Exception as e:
            file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
            self.logger.log(file, "Error while creating table: %s " % e)
            file.close()
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Closed %s database successfully" % DatabaseName)
            file.close()
            raise e

    def insertIntoTableGoodData(self, Database):

        conn = self.dataBaseConnection(Database)
        goodFilePath = self.goodFilePath
        badFilePath = self.badFilePath
        only_files = [f for f in listdir(goodFilePath)]
        log_file = open("Training_Logs/DbInsertLog.txt", 'a+')

        for file in only_files:
            try:
                with open(goodFilePath + '/' + file, "r") as f:
                    # next(f)
                    reader = csv.reader(f, delimiter="\n")
                    for line in enumerate(reader):
                        entries = tuple(line[1][0].split(sep=','))
                        # for list_ in line[1].split(sep=','):
                        try:
                            conn.execute('INSERT OR REPLACE INTO Good_Raw_Data values {values}'.format(values=entries))
                            conn.commit()
                        except Exception as e:
                            raise e
                    self.logger.log(log_file, " %s: File loaded successfully!!" % file)

            except Exception as e:

                conn.rollback()
                self.logger.log(log_file, "Error while creating table: %s " % e)
                shutil.move(goodFilePath + '/' + file, badFilePath)
                self.logger.log(log_file, "File Moved Successfully %s" % file)
                log_file.close()
                conn.close()

        conn.close()
        log_file.close()

    def selectingDatafromtableintocsv(self, Database):

        fileFromDb = 'Training_FileFromDB/'
        fileName = 'InputFile.csv'
        log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
        try:
            conn = self.dataBaseConnection(Database)
            sqlSelect = "SELECT *  FROM Good_Raw_Data"
            cursor = conn.cursor()

            cursor.execute(sqlSelect)

            results = cursor.fetchall()
            # Get the headers of the csv file
            # headers = [i[0] for i in cursor.description]

            # Make the CSV output directory
            if not os.path.isdir(fileFromDb):
                os.makedirs(fileFromDb)

            # Open CSV file for writing.
            csvFile = csv.writer(open(fileFromDb + fileName, 'w', newline=''), delimiter=',',
                                 lineterminator='\r\n', quoting=csv.QUOTE_ALL, escapechar='\\')

            # Add the headers and data to the CSV file.
            # csvFile.writerow(headers)
            csvFile.writerows(results)

            self.logger.log(log_file, "File exported successfully!!!")
            log_file.close()

        except Exception as e:
            self.logger.log(log_file, "File exporting failed. Error : %s" % e)
            log_file.close()
