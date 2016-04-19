import logging

class Logable(object):
    """
    A class which can print to the log

    log_mode = 0 - Log mod: log_mode = 0 log to console, log_mode = 1 log to file,
    log_mode = 2 no log.
    """
    def __init__(self, log_mode=0):
        # log_mode 0 to console, 1 to file
        self.log_mode = log_mode

    def write_log(self, log_text):
        """ Write log by print() or logger """

        if self.log_mode == 0:
            try:
                print(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")
        elif self.log_mode == 1:
            # Create log_file if not exist.
            if self.log_file == 0:
                self.log_file = 1
                now_time = datetime.datetime.now()
                self.log_full_path = '%s%s_%s.log' % (self.log_file_path,
                                     self.user_login,
                                     now_time.strftime("%d.%m.%Y_%H:%M"))
                formatter = logging.Formatter('%(asctime)s - %(name)s '
                            '- %(message)s')
                self.logger = logging.getLogger(self.user_login)
                self.hdrl = logging.FileHandler(self.log_full_path, mode='w')
                self.hdrl.setFormatter(formatter)
                self.logger.setLevel(level=logging.INFO)
                self.logger.addHandler(self.hdrl)
            # Log to log file.
            try:
                self.logger.info(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")
