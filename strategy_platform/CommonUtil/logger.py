import logging
import os
from datetime import datetime
import utildomain as ud
from logging.handlers import RotatingFileHandler


class StaticLog:
    app_logger: logging.Logger(name='') = None


class AppLog:
    @staticmethod
    def logger():
        if not StaticLog.app_logger:
            create_logger()

        return StaticLog.app_logger


def create_logger(output_to_console=False, output_to_logfile=False, logging_level=logging.INFO):
    if not StaticLog.app_logger:
        # file path
        dir_path = os.path.join(os.getcwd(), 'log')
        ud.folder_exists_or_create(dir_path)
        filename = '{:%Y-%m-%d}'.format(datetime.now()) + '.log'
        log_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(funcName)s(%(lineno)d)] [%(threadName)s] %(message)s')

        all_log = logging.getLogger('root')
        all_log.setLevel(logging_level)

        if output_to_logfile:
            file_handler = RotatingFileHandler(
                filename=os.path.join(dir_path, filename),
                mode='a',
                maxBytes=30 * 1024 * 1024,
                backupCount=100,
            )
            file_handler.setFormatter(log_formatter)
            all_log.addHandler(file_handler)

        if output_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            all_log.addHandler(console_handler)

        logging.captureWarnings(True)  # catch py waring message

        StaticLog.app_logger = all_log
