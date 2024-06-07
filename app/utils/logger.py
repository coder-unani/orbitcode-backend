from datetime import datetime


class Logger:

    LOG_PATH = "data/log/{}_{}_{}.log".format(datetime.now().year, datetime.now().month, datetime.now().day)

    @classmethod
    def write_log(cls, log_type, object_name, log_message):
        log_message = "[{}][{}][{}] - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"), object_name, log_type,
                                                 log_message)
        with open(cls.LOG_PATH, "a") as file:
            file.write(log_message + "\n")

    @classmethod
    def info_log(cls, object_name, message):
        cls.write_log("info", object_name, message)

    @classmethod
    def error_log(cls, object_name, message):
        cls.write_log("error", object_name, message)


