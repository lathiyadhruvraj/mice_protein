import glob
# from wsgiref import simple_server
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, send_file
from flask import Response
import os
from prediction_Validation_Insertion import pred_validation
from predictFromModel import prediction
from trainingModel import TrainModel
from training_validation_insertion import TrainValidation

# os.putenv('LANG', 'en_US.UTF-8')
# os.putenv('LC_ALL', 'en_US.UTF-8')

application = Flask(__name__)
app = application


app.config["FILE_DOWNLOAD"] = os.path.join(os.getcwd(), "Prediction_Output_File")

app.config["FILE_UPLOADS"] = os.path.join(os.getcwd(), "Prediction_Custom_Files")

predict = 0
upload = 0


@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')


@app.route("/predict", methods=['GET', 'POST'])
@app.route("/predict_default", methods=['GET', 'POST'])
def predictRouteClient():
    global predict, upload
    try:
        if request.json is not None:
            path = request.json['filepath']

            pred_val = pred_validation(path)  # object initialization

            pred_val.prediction_validation()  # calling the prediction_validation function

            pred = prediction(path)  # object initialization

            # predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at %s!!!" % path)

        elif request.form is not None:
            
            if (request.form['button'] == "Predict My File") and (upload == 1):
                predict = 1
                upload = 0
                print('custom call')
                path = "Prediction_Custom_Files"

                pred_val = pred_validation(path)  # object initialization

                pred_val.prediction_validation()  # calling the prediction_validation function

                pred = prediction(path)  # object initialization

                # predicting for dataset present in database
                path, res_head = pred.predictionFromModel()
                message = "Prediction File created at " + str(path)

                # return Response("Prediction File created at %s!!!" % path)
                return render_template('index.html', message=message, head="TOP FIVE PREDICTED ROWS",
                                       result=res_head)

            elif request.form['button'] == "Predict Default Available File":
                predict = 1
                upload = 0
                print('default call')
                path = "Prediction_Batch_Files"

                pred_val = pred_validation(path)  # object initialization

                pred_val.prediction_validation()  # calling the prediction_validation function

                pred = prediction(path)  # object initialization

                # predicting for dataset present in database
                path, res_head = pred.predictionFromModel()
                message = "Prediction File created at " + str(path)
                # return Response("Prediction File created at %s!!!" % path)
                return render_template('index.html', message=message, head="TOP FIVE PREDICTED ROWS",
                                       result=res_head)
            message = "UPLOAD FILE TO PREDICT FILE OR CHOOSE DEFAULT FILE"
            return render_template('index.html', message=message)

    except ValueError:
        return Response("Error Occurred! %s" % ValueError)
    except KeyError:
        return Response("Error Occurred! %s" % KeyError)
    except Exception as e:
        warn = e
        predict = 0
        message = "MAKE SURE YOU ARE CHOOSING A FILE BEFORE CLCIKING UPLOAD BUTTON AND CHECK PROPER FILE FORMAT AS WELL"
        return render_template('index.html', warn=warn, message=message)


@app.route("/train", methods=['GET', 'POST'])
def trainRouteClient():
    try:
        if request.json['folderPath'] is not None:
            path = request.json['folderPath']
            # path = "Training_Batch_Files"
            # path = json.loads(path_str)

            train_valObj = TrainValidation(path)
            train_valObj.train_validation()

            trainModelObj = TrainModel()
            trainModelObj.trainingModel()

    except ValueError:
        return Response("Error Occurred! %s" % ValueError)

    except KeyError:
        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:
        return Response("Error Occurred! %s" % e)

    return Response("Training successful!!")


@app.route("/upload_custom_files", methods=["POST"])
def upload_files():
    try:
        if request.method == "POST":
            global predict, upload
            # predict = 1
            upload = 1
            f = request.files["file"]
            files = glob.glob("Prediction_Custom_Files/*")
            for fn in files:
                os.remove(fn)

            if request.files and (f.filename.split(".")[1] == "xls"):
                f.save(os.path.join(app.config["FILE_UPLOADS"], secure_filename(f.filename)))
                print("File Saved")
                message = str(f.filename) + " Loaded Successfully. Press Predict My File and wait a minute."
                warn = "DO NOT REFRESH/DO NOT PRESS BUTTONS while YOUR FILE IN PROCESS"

                return render_template('index.html', message=message, warn=warn)

            else:
                message = " Only excel file allowed (.xls)"
                return render_template('index.html', message=message)

        return render_template('index.html', message="CHOOSE A FILE")

    except Exception as e:
        message = " File Not Uploaded. Make sure you are selecting a file"
        warn = e
        return render_template('index.html', message=message, warn=warn)


@app.route("/download", methods=['POST'])
def download_file():
    global predict
    try:
        if predict:
            predict = 0
            fname = "Predictions.csv"
            file = os.path.join(app.config["FILE_DOWNLOAD"], fname)
            if os.path.isfile(file):
                return send_file(file, mimetype='text/csv', as_attachment=True, attachment_filename=fname)

        else:
            head = "PREDICTION FILE NOT AVAILABLE," \
                   " UPLOAD YOUR FILE THEN PRESS PREDICT MY FILE OR PRESS PREDICT AVAILABLE FILE"
            return render_template('index.html', head=head)

    except Exception as e:
        warn = e
        return render_template('index.html', warn=warn)


# port = int(os.getenv("PORT", 5001))
if __name__ == "__main__":
    app.run(debug=True)
    # host = '0.0.0.0'
    # httpd = simple_server.make_server(host, port, app)
    # print("Serving on %s %d" % (host, port))
    # httpd.serve_forever()
