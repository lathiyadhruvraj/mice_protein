from Logging_Layer import logger
from Training_RawData_Validation.rawValidation import RawDataValidation
from DataTypeValidation_Insertion_Training.dataTypeValidation import dBOperation
from DataStax_Astra_Connect.connect_database import Cassandra
import os

class TrainValidation:

    def __init__(self, path):
        self.raw_data = RawDataValidation(path)
        self.dbOperations = dBOperation()
        self.file_object = open("Training_Logs/Training_Main_Log.txt", 'a+')
        self.cassandra = Cassandra(self.file_object)
        self.log_writer = logger.app_logger()

    def train_validation(self):
        try:
            self.log_writer.log(self.file_object, 'Start of Validation on files for prediction!!')

            #getting files from cassandra
            self.cassandra.connect_datastax("mice_protein")

            data = self.cassandra.fetch_data()

            path = os.path.join(os.getcwd(), 'Training_Batch_Files')
            self.cassandra.data_to_excel(data=data, path=path)

            # extracting values from prediction schema
            LengthOfDateStampInFile, LengthOfTimeStampInFile, ColName, noofcolumns = self.raw_data.valuesFromSchema()

            # getting the regex defined to validate filename
            regex = self.raw_data.manualRegexCreation()
            # validating filename of prediction files
            self.raw_data.validationFileNameRaw(regex, LengthOfDateStampInFile, LengthOfTimeStampInFile)

            # validating column length in the file
            self.raw_data.validateColumnLength(noofcolumns)
            # validating if any column has all values missing
            self.raw_data.validateMissingValuesInWholeColumn()
            self.log_writer.log(self.file_object, "Raw Data Validation Complete!!")

            self.log_writer.log(self.file_object,
                                "Creating Training_Database and tables on the basis of given schema!!!")

            # create database with given name, if present open the connection! Create table with columns given in schema
            self.dbOperations.createTableDb('Training', ColName)
            self.log_writer.log(self.file_object, "Table creation Completed!!")
            self.log_writer.log(self.file_object, "Insertion of Data into Table started!!!!")

            # insert csv files in the table
            self.dbOperations.insertIntoTableGoodData('Training')
            self.log_writer.log(self.file_object, "Insertion in Table completed!!!")
            self.log_writer.log(self.file_object, "Deleting Good Data Folder!!!")

            # Delete the good data folder after loading files in table
            self.raw_data.deleteExistingGoodDataTrainingFolder()
            self.log_writer.log(self.file_object, "Good_Data folder deleted!!!")
            self.log_writer.log(self.file_object, "Moving bad files to Archive and deleting Bad_Data folder!!!")

            # Move the bad files to archive folder
            self.raw_data.moveBadFilesToArchiveBad()
            self.log_writer.log(self.file_object, "Bad files moved to archive!! Bad folder Deleted!!")
            self.log_writer.log(self.file_object, "Validation Operation completed!!")
            self.log_writer.log(self.file_object, "Extracting csv file from table")

            # export data in table to csv file
            self.dbOperations.selectingDatafromtableintocsv('Training')
            self.file_object.close()
            print("VALIDATION FINISH")

        except Exception as e:
            print("EXCEPTION", e)
            raise e
