from datetime import datetime


class app_logger:

    def __init__(self):
        pass

    def log(self, file_object, log_message):
        now = datetime.now()
        date = now.date()
        current_time = now.strftime("%H:%M:%S")
        file_object.write(
            str(date) + "/" + str(current_time) + "\t\t" + log_message + "\n")
