from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import warnings
from sklearn.metrics import precision_score
warnings.filterwarnings("ignore")


class Model_Finder:

    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object
        self.clf = RandomForestClassifier()
        self.xgb = XGBClassifier(objective='binary:logistic', use_label_encoder=False)

    def get_best_params_for_random_forest(self, train_x, train_y):

        self.logger_object.log(self.file_object,
                               'Entered the get_best_params_for_random_forest method of the Model_Finder class')
        try:
            # initializing with different combination of parameters
            param_grid = {"n_estimators": [10, 50, 100, 130], "criterion": ['gini', 'entropy'],
                          "max_depth": range(2, 4, 1), "max_features": ['auto', 'log2']}

            # Creating an object of the Grid Search class
            grid = GridSearchCV(estimator=self.clf, param_grid=param_grid, cv=5, verbose=3)
            # finding the best parameters
            grid.fit(train_x, train_y)

            # extracting the best parameters
            criterion = grid.best_params_['criterion']
            max_depth = grid.best_params_['max_depth']
            max_features = grid.best_params_['max_features']
            n_estimators = grid.best_params_['n_estimators']

            # creating a new model with the best parameters
            self.clf = RandomForestClassifier(n_estimators=n_estimators, criterion=criterion,
                                              max_depth=max_depth, max_features=max_features)
            # training the mew model
            self.clf.fit(train_x, train_y)
            self.logger_object.log(self.file_object, 'Random Forest best params: ' + str(grid.best_params_) +
                                   '. Exited the get_best_params_for_random_forest method of the Model_Finder class')

            return self.clf
        except Exception as e:
            self.logger_object.log(self.file_object, 'Exception occurred in get_best_params_for_random_forest method '
                                                     'of the Model_Finder class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object, 'Random Forest Parameter tuning  failed. Exited the '
                                                     'get_best_params_for_random_forest method '
                                                     'of the Model_Finder class')
            raise Exception()

    def get_best_params_for_xgboost(self, train_x, train_y):

        self.logger_object.log(self.file_object,
                               'Entered the get_best_params_for_xgboost method of the Model_Finder class')
        try:
            # initializing with different combination of parameters
            param_grid_xgboost = {

                'learning_rate': [0.5, 0.1, 0.01, 0.001],
                'max_depth': [3, 5, 10, 20],
                'n_estimators': [10, 50, 100, 200]

            }
            # Creating an object of the Grid Search class
            grid = GridSearchCV(XGBClassifier(objective='binary:logistic'), param_grid_xgboost, verbose=3, cv=5)
            # finding the best parameters
            grid.fit(train_x, train_y)

            # extracting the best parameters
            learning_rate = grid.best_params_['learning_rate']
            max_depth = grid.best_params_['max_depth']
            n_estimators = grid.best_params_['n_estimators']

            # creating a new model with the best parameters
            self.xgb = XGBClassifier(learning_rate=learning_rate, max_depth=max_depth, n_estimators=n_estimators)
            # training the mew model
            self.xgb.fit(train_x, train_y)
            self.logger_object.log(self.file_object, 'XGBoost best params: ' + str(grid.best_params_) +
                                   '. Exited the get_best_params_for_xgboost method of the Model_Finder class')
            return self.xgb
        except Exception as e:
            self.logger_object.log(self.file_object, 'Exception occurred in get_best_params_for_xgboost method of the '
                                                     'Model_Finder class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object, 'XGBoost Parameter tuning  failed. Exited the '
                                                     'get_best_params_for_xgboost method of the Model_Finder class')
            raise Exception()

    def get_best_model(self, train_x, train_y, test_x, test_y):

        self.logger_object.log(self.file_object,
                               'Entered the get_best_model method of the Model_Finder class')
        # create best model for XGBoost
        try:
            precisionScore_rf_macro_avg = 0
            precisionScore_xgb_macro_avg = 0

            xgboost = self.get_best_params_for_xgboost(train_x, train_y)
            prediction_xgboost = xgboost.predict(test_x)  # Predictions using the XGBoost Model

            if len(test_y.unique()) == 1:  # if there is only one label in y, then roc_auc_score returns error. We
                # will use accuracy in that case
                xgboost_score = accuracy_score(test_y, prediction_xgboost)
                self.logger_object.log(self.file_object, 'Accuracy for XGBoost:' + str(xgboost_score))  # Log AUC
            else:
                precisionScore_xgb_macro_avg = precision_score(test_y, prediction_xgboost, average='macro')
                # self.xgboost_score = roc_auc_score(test_y, self.prediction_xgboost, multi_class='ovr',
                #                                   average='macro')  # AUC for XGBoost
                self.logger_object.log(self.file_object, 'precision_score for XGBoost:' + str(
                    precisionScore_xgb_macro_avg))  # Log AUC

            # create best model for Random Forest

            random_forest = self.get_best_params_for_random_forest(train_x, train_y)
            prediction_random_forest = random_forest.predict(
                test_x)  # prediction using the Random Forest Algorithm

            if len(test_y.unique()) == 1:  # if there is only one label in y, then roc_auc_score returns error. We
                # will use accuracy in that case
                random_forest_score = accuracy_score(test_y, prediction_random_forest)
                self.logger_object.log(self.file_object, 'Accuracy for RF:' + str(random_forest_score))
            else:
                precisionScore_rf_macro_avg = precision_score(test_y, prediction_random_forest, average='macro')

                # self.random_forest_score = roc_auc_score(test_y, self.prediction_random_forest, multi_class='ovr',
                #                                         average='macro')  # AUC for Random Forest
                self.logger_object.log(self.file_object,
                                       'precision_score for RF:' + str(precisionScore_rf_macro_avg))

            # comparing the two models
            if precisionScore_rf_macro_avg < precisionScore_xgb_macro_avg:
                return 'XGBoost', xgboost
            else:
                return 'RandomForest', random_forest

        except Exception as e:
            self.logger_object.log(self.file_object, 'Exception occurred in get_best_model method of the Model_Finder '
                                                     'class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Model Selection Failed. Exited the get_best_model method of the Model_Finder class')
            raise Exception()
