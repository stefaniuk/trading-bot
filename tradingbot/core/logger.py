import os
import re
import logging
import logging.config
from datetime import datetime

from .color import *

conv = {'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL}


class logger(object):
    def __init__(self, level):
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))
        logger = logging.getLogger('tradingbot')
        logger.setLevel(conv[level])

    def debug(self, s):
        logging.info(printer.process('- ' + re.match(r'\d+:\d+:\d+',
            str(datetime.now().time())).group(0) + ' - ' + s))
    
    def info(self, s):
        logging.info(printer.info('- ' + re.match(r'\d+:\d+:\d+',
            str(datetime.now().time())).group(0) + ' - ' + s))
    
    def warning(self, s):
        logging.info(printer.warning('- ' + re.match(r'\d+:\d+:\d+',
            str(datetime.now().time())).group(0) + ' - ' + s))
    
    def error(self, s):
        logging.info(printer.error('- ' + re.match(r'\d+:\d+:\d+',
            str(datetime.now().time())).group(0) + ' - ' + s))
    
    def critical(self, s):
        logging.info(printer.critical('- ' + re.match(r'\d+:\d+:\d+',
            str(datetime.now().time())).group(0) + ' - ' + s))