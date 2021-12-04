import json
import os
from datetime import datetime
import pandas
import shutil
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader_prediction
from Logging_Layer import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation 

class prediction:

    def __init__(self, path):
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.app_logger()
        self.pred_data_val = Prediction_Data_validation(path)

    def predictionFromModel(self):
        
        try:
            only_files = [f for f in os.listdir("Prediction_FileFromDB/")]

            for file in only_files:
                print(file)
                self.log_writer.log(self.file_object, 'Start of Prediction')
                data_getter = data_loader_prediction.Data_Getter_Pred(self.file_object, self.log_writer, file)
                data = data_getter.get_data()

                preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
                data = preprocessor.remove_columns(data, ['MouseID', 'Genotype', 'Treatment', 'Behavior'])

                is_null_present = preprocessor.is_null_present(data)
                if is_null_present:
                    data = preprocessor.impute_missing_values(data)

                cols_to_drop = preprocessor.get_columns_with_zero_std_deviation(data)
                X = preprocessor.remove_columns(data, cols_to_drop)

                X1 = preprocessor.remove_outliers(X)

                preprocessor.reduce_dim_and_plot(X1, "pca_pred_"+'_'.join(str.split("_")[1:])+".png")

                # _, count = preprocessor.cal_components(ratio, 0.96)

                new_data = preprocessor.pca_with_comp(X1, 11)
                # data=data.to_numpy()
                file_loader = file_methods.File_Operation(self.file_object, self.log_writer)
                kmeans = file_loader.load_model('KMeans')

                # Code changed

                clusters = kmeans.predict(new_data)  # drops the first column for cluster prediction
                new_data['cluster_no'] = clusters
                no_of_clusters = new_data['cluster_no'].unique()

                results = []
                for i in no_of_clusters:
                    cluster_data = new_data[new_data['cluster_no'] == i]
                    cluster_data = cluster_data.drop(['cluster_no'], axis=1)
                    model_name = file_loader.find_correct_model_file(i)
                    model = file_loader.load_model(model_name)
                    for val in (model.predict(cluster_data)):
                        results.append(val)

                with open(os.path.join(os.getcwd(), 'Output_Label.json')) as json_file:
                    js_obj = json.load(json_file)
                    names = [js_obj[str(key)] for key in results]

                results = pandas.DataFrame(results, columns=['Prediction'])
                results['Label'] = names
           
                now = datetime.now()
                current_time = str((now.strftime("%H:%M:%S")).replace(':', "_")) + "_"

                path = os.path.join("Prediction_Output_File", current_time + ("_".join(str(file).split("_")[1:]).split(".")[0])+".csv")
                # path = "Prediction_Output_File/Prediction"+ current_time +".csv"
                results.to_csv(path, header=True, mode='w+')  # appends result to prediction file
                self.log_writer.log(self.file_object, 'End of Prediction')

                #removing files from directories
                shutil.rmtree("Prediction_Batch_Files")
                shutil.rmtree("Prediction_Custom_Files")
                os.mkdir(os.path.join(os.getcwd(), "Prediction_Batch_Files"))
                os.mkdir(os.path.join(os.getcwd(), "Prediction_Custom_Files"))
        
        except Exception as ex:
            print(ex)
            self.log_writer.log(self.file_object, 'Error occurred while running the prediction!! Error:: %s' % ex)
            raise ex
        return path
