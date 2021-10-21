import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder


# from sklearn.preprocessing import StandardScaler


class Preprocessor:

    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object

    def remove_columns(self, data, columns):

        self.logger_object.log(self.file_object, 'Entered the remove_columns method of the Preprocessor class')
        # self.data = data
        # self.columns = columns
        try:
            useful_data = data.drop(labels=columns, axis=1)  # drop the labels specified in the columns
            self.logger_object.log(self.file_object,
                                   'Column removal Successful.Exited the remove_columns method of the Preprocessor '
                                   'class')
            return useful_data
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in remove_columns method of the Preprocessor class. Exception '
                                   'message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Column removal Unsuccessful. Exited the remove_columns method of the Preprocessor '
                                   'class')
            raise Exception()

    def separate_label_feature(self, data, label_column_name):

        self.logger_object.log(self.file_object, 'Entered the separate_label_feature method of the Preprocessor class')
        try:
            X = data.drop(labels=label_column_name,
                          axis=1)  # drop the columns specified and separate the feature columns
            Y = data[label_column_name]  # Filter the Label columns
            self.logger_object.log(self.file_object,
                                   'Label Separation Successful. Exited the separate_label_feature method of the '
                                   'Preprocessor class')
            return X, Y
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in separate_label_feature method of the Preprocessor class. '
                                   'Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Label Separation Unsuccessful. Exited the separate_label_feature method of the '
                                   'Preprocessor class')
            raise Exception()

    def is_null_present(self, data):

        self.logger_object.log(self.file_object, 'Entered the is_null_present method of the Preprocessor class')
        null_present = False
        try:
            null_counts = data.isna().sum()  # check for the count of null values per column
            for i in null_counts:
                if i > 0:
                    null_present = True
                    break
            if null_present:  # write the logs to see which columns have null values
                dataframe_with_null = pd.DataFrame()
                dataframe_with_null['columns'] = data.columns
                dataframe_with_null['missing values count'] = np.asarray(data.isna().sum())
                dataframe_with_null.to_csv('preprocessing_data/null_values.csv')
                # storing the null column information to file
            self.logger_object.log(self.file_object,
                                   'Finding missing values is a success.Data written to the null values file. Exited '
                                   'the is_null_present method of the Preprocessor class')
            return null_present
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in is_null_present method of the Preprocessor class. Exception '
                                   'message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Finding missing values failed. Exited the is_null_present method of the '
                                   'Preprocessor class')
            raise Exception()

    def impute_missing_values(self, data):

        self.logger_object.log(self.file_object, 'Entered the impute_missing_values method of the Preprocessor class')
        # self.data = data
        try:
            imputer = KNNImputer(n_neighbors=3, weights='uniform', missing_values=np.nan)
            new_array = imputer.fit_transform(data)  # impute the missing values
            # convert the nd-array returned in the step above to a Dataframe
            new_data = pd.DataFrame(data=new_array, columns=data.columns)
            self.logger_object.log(self.file_object,
                                   'Imputing missing values Successful. Exited the impute_missing_values method of '
                                   'the Preprocessor class')
            return new_data
        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in impute_missing_values method of the Preprocessor class. '
                                   'Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Imputing missing values failed. Exited the impute_missing_values method of the '
                                   'Preprocessor class')
            raise Exception()

    def get_columns_with_zero_std_deviation(self, data):

        self.logger_object.log(self.file_object,
                               'Entered the get_columns_with_zero_std_deviation method of the Preprocessor class')
        columns = data.columns
        data_n = data.describe()
        col_to_drop = []
        try:
            for x in columns:
                if data_n[x].std() == 0:  # check if standard deviation is zero
                    col_to_drop.append(x)  # prepare the list of columns with standard deviation zero
            self.logger_object.log(self.file_object,
                                   'Column search for Standard Deviation of Zero Successful. Exited the '
                                   'get_columns_with_zero_std_deviation method of the Preprocessor class')
            return col_to_drop

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in get_columns_with_zero_std_deviation method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Column search for Standard Deviation of Zero Failed. Exited the '
                                   'get_columns_with_zero_std_deviation method of the Preprocessor class')
            raise Exception()

    def reduce_dim_and_plot(self, data, file_name):
        self.logger_object.log(self.file_object,
                               'Entered the reduce_dim_and_plot method of the Preprocessor class')
        try:
            pca = PCA()
            pca.fit_transform(data)

            plt.figure(figsize=(13, 6))
            plt.plot(np.cumsum(pca.explained_variance_ratio_), c='b', label='Line After Removing outliers')

            plt.xlabel('Number of Components')
            plt.ylabel('Variance (%)')  # for each component
            plt.title('Explained Variance')
            plt.grid()
            plt.legend()

            plot_dir = "plots"
            os.makedirs(plot_dir, exist_ok=True)  # ONLY CREATE IF MODEL_DIR DOESNT EXISTS
            plotPath = os.path.join(plot_dir, file_name)  # model/filename
            plt.savefig(plotPath)
            self.logger_object.log(self.file_object, f'Exited the reduce_dim method and saved plot at {plotPath}')

            return pca.explained_variance_ratio_

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in reduce_dim method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))

            raise Exception()

    def remove_outliers(self, data):
        try:
            self.logger_object.log(self.file_object,
                                   'Entered the remove_outliers method of the Preprocessor class')
            for col in data.columns:
                X = np.sort(data[col])

                Q1 = np.percentile(X, 25, interpolation='midpoint')
                Q3 = np.percentile(X, 75, interpolation='midpoint')
                lower_bound = Q1 - (1.5 * (Q3 - Q1))
                upper_bound = Q3 + (1.5 * (Q3 - Q1))

                mean = np.mean(data[col])
                median = np.median(data[col])

                if (min(data[col]) < lower_bound) or (max(data[col]) > upper_bound):
                    data[col] = np.where(data[col] < lower_bound, mean, data[col])
                    data[col] = np.where(data[col] > upper_bound, median, data[col])

            self.logger_object.log(self.file_object,
                                   'Exited the remove_outliers method of the Preprocessor class')
            return data

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in remove_outliers method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))
            raise Exception()

    def cal_components(self, ratio, score):
        try:
            self.logger_object.log(self.file_object, 'Entered the cal_components method of the Preprocessor class')

            total = 0.0
            count = 0
            copy = np.sort(ratio).tolist()

            for i in range(len(copy), 0, -1):
                if total < score:
                    total = total + copy[i - 1]
                    count += 1
                else:
                    break

            self.logger_object.log(self.file_object, 'Exited the cal_components method of the Preprocessor class')

            return total, count

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in cal_components method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))
            raise Exception()

    def pca_with_comp(self, data, no):
        try:
            self.logger_object.log(self.file_object, 'Entered the pca_with_comp method of the Preprocessor class')

            new_pca = PCA(no)
            components = pd.DataFrame(new_pca.fit_transform(data))
            self.logger_object.log(self.file_object, 'Exited  the pca_with_comp method of the Preprocessor class')

            return components

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in pca_with_comp method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))
            raise Exception()

    def encode_label(self, Y):
        try:
            self.logger_object.log(self.file_object, 'Entered the encode_label method of the Preprocessor class')

            le = LabelEncoder()

            self.logger_object.log(self.file_object, 'Exited  the encode_label method of the Preprocessor class')

            return le.fit_transform(Y)

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in encode_label method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))
            raise Exception()
