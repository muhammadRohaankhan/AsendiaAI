import logging
import os

def setup_logger(log_file='logs/query_log.txt'):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logger = logging.getLogger('QueryLogger')
    logger.setLevel(logging.INFO)
    # Remove all existing handlers to avoid CLI output
    logger.handlers = []
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
