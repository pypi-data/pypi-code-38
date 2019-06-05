import datetime


class NullFileLog:
    def __init__(self):
        pass

    def info(self, message):
        print(message)


class Log:

    def __init__(self, file_full_name):
        # type: (str) -> Log
        """
        Creates new instance of Log object.
        :param file_full_name: Path to the log file.
        """
        self.fs = open(file_full_name, 'a')

    def info(self, message):
        # type: (str) -> None
        """
        Writes the message to the log.
        :param message: Message string.
        """
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        log_entry = '[{time_stamp}] {message}'.format(message=message, time_stamp=time_stamp)
        self.fs.write('{log_entry}\n'.format(log_entry=log_entry))
        print(log_entry)

    def __delete__(self, instance):
        self.fs.flush()
        self.fs.close()
