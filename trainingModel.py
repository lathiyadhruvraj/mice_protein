# Doing the necessary imports
import copy
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from data_ingestion import data_loader
from data_preprocessing import preprocessing
from data_preprocessing import clustering
from best_model_finder import tuner
from file_operations import file_methods
from Logging_Layer import logger


class TrainModel:

    def __init__(self):
        self.log_writer = logger.app_logger()
        self.file_object = open("Training_Logs/ModelTrainingLog.txt", 'a+')

    def trainingModel(self):
        # Logging the start of Training
        self.log_writer.log(self.file_object, 'Start of Training')
        try:
            # Getting the data from the source
            data_getter = data_loader.Data_Getter(self.file_object, self.log_writer)
            data = data_getter.get_data()

            """doing the data preprocessing"""

            preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
            data = preprocessor.remove_columns(data, ['MouseID', 'Genotype', 'Treatment', 'Behavior'])
            # removed the columns that doesn't contribute to prediction. Anyway we are using PCA
            output_col = data['class']
            y_string = copy.deepcopy(output_col)
            # create separate features and labels
            X, Y = preprocessor.separate_label_feature(data, label_column_name='class')
            Y = preprocessor.encode_label(Y)

            uni = np.unique(Y)
            dic = {}
            class_encoded_value = pd.DataFrame(zip(y_string, Y), columns=['names', 'values'])
            for i in uni:
                dic[int(i)] = class_encoded_value[class_encoded_value.values == i].names.unique()[0]

            path = "C://Users//Dhruvraj//Desktop//INEURON_INTERNSHIP//Mice_Protein_Expression//code//"
            out_file = open(path + "Output_Label.json", "w")
            json.dump(dic, out_file, indent=4)
            out_file.close()

            # check if missing values are present in the dataset
            is_null_present = preprocessor.is_null_present(X)

            # if missing values are there, replace them appropriately.
            if is_null_present:
                X = preprocessor.impute_missing_values(X)  # missing value imputation

            # check further which columns do not contribute to predictions
            # if the standard deviation for a column is zero, it means that the column has constant values
            # and they are giving the same output both for good and bad sensors
            # prepare the list of such columns to drop
            cols_to_drop = preprocessor.get_columns_with_zero_std_deviation(X)

            # drop the columns obtained above
            X = preprocessor.remove_columns(X, cols_to_drop)

            X1 = preprocessor.remove_outliers(X)

            ratio = preprocessor.reduce_dim_and_plot(X1, "pca.png")

            _, count = preprocessor.cal_components(ratio, 0.96)

            new_X = preprocessor.pca_with_comp(X1, count)

            """ Applying the clustering approach"""

            kmeans = clustering.KMeansClustering(self.file_object, self.log_writer)  # object initialization.
            number_of_clusters = kmeans.elbow_plot(new_X)  # using the elbow plot to find the number of optimum clusters

            # Divide the data into clusters
            X = kmeans.create_clusters(new_X, number_of_clusters)

            # create a new column in the dataset consisting of the corresponding cluster assignments.
            X['Labels'] = Y

            # getting the unique clusters from our dataset
            list_of_clusters = X['Cluster'].unique()
            print(list_of_clusters)

            """parsing all the clusters and looking for the best ML algorithm to fit on individual cluster"""

            for i in list_of_clusters:
                cluster_data = X[X['Cluster'] == i]  # filter the data for one cluster

                # Prepare the feature and Label columns
                cluster_features = cluster_data.drop(['Labels', 'Cluster'], axis=1)
                cluster_label = cluster_data['Labels']

                # splitting the data into training and test set for each cluster one by one
                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=0.30,
                                                                    random_state=355)
                # print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)

                model_finder = tuner.Model_Finder(self.file_object, self.log_writer)  # object initialization

                # getting the best model for each of the clusters
                best_model_name, best_model = model_finder.get_best_model(x_train, y_train, x_test, y_test)

                # saving the best model to the directory.
                file_op = file_methods.File_Operation(self.file_object, self.log_writer)
                file_op.save_model(best_model, best_model_name + str(i))

            # logging the successful Training
            self.log_writer.log(self.file_object, 'Successful End of Training')
            self.file_object.close()

        except Exception as e:
            # logging the unsuccessful Training
            self.log_writer.log(self.file_object, e)
            self.log_writer.log(self.file_object, 'Unsuccessful End of Training')
            self.file_object.close()
            raise Exception()
