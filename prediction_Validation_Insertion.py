from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
from DataTypeValidation_Insertion_Prediction.DataTypeValidationPrediction import dBOperation
from Logging_Layer import logger
import os
from DataStax_Astra_Connect.connect_database import Cassandra
class pred_validation:
    def __init__(self, path):
        self.dir = path
        self.raw_data = Prediction_Data_validation(path)
        self.dBOperation = dBOperation()
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.cassandra = Cassandra(self.file_object)
        self.log_writer = logger.app_logger()

    def prediction_validation(self):

        try:

            self.log_writer.log(self.file_object, 'Start of Validation on files for prediction!!')
            
            if self.dir == "Prediction_Batch_Files":
                #getting files from cassandra
                self.cassandra.connect_datastax("mice_protein")

                data = self.cassandra.fetch_data()

                path = os.path.join(os.getcwd(), 'Prediction_Batch_Files')
                self.cassandra.data_to_excel(data=data, path=path)
            else:
                print("Skipped datastax connection")

            # extracting values from prediction schema
            LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, noofcolumns = self.raw_data.valuesFromSchema()
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
                                "Creating Prediction_Database and tables on the basis of given schema!!!")
            # create database with given name, if present open the connection! Create table with columns given in schema
            self.dBOperation.createTableDb(column_names)
            self.log_writer.log(self.file_object, "Table creation Completed!!")
            self.log_writer.log(self.file_object, "Insertion of Data into Table started!!!!")
            # insert csv files in the table
            self.dBOperation.insertIntoTableGoodData()
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
            
            # deletes the existing files from Prediction_Output_File and Prediction_FileFromDB dirs from last run!
            self.raw_data.deletePredictedFiles() 
            self.log_writer.log(self.file_object, 'Deleted Old Files From Directories Prediction_Output_File, Prediction_FileFromDB and plots')
            # export data in table to csv file
            self.dBOperation.selectingDatafromtableintocsv()

        except Exception as e:
            raise e
