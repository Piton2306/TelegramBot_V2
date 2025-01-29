import logging
import os

def setup_logging(log_dir='logs', log_file='app.log', logger_name='root'):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

        file_handler = logging.FileHandler(os.path.join(log_dir, log_file), 'a', 'utf-8')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
