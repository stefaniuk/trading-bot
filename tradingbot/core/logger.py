# -*- coding: utf-8 -*-

"""
tradingbot.core.logger
~~~~~~~~~~~~~~

This module customize logging.
"""

from os import path
import sys
import re
import logging
import logging.config
from datetime import datetime
from .color import *


class logger(object):
    logging.config.fileConfig(
        path.join(path.dirname(__file__), 'logging.conf'))
    logging.getLogger().setLevel(getattr(logging, 'DEBUG'))

    def setlevel(level):
        logging.getLogger().setLevel(getattr(logging, level.upper()))

    def __get_date():
        return re.match(r'\d+:\d+:\d+', str(datetime.now().time())).group(0)

    def debug(s):
        logging.debug(printer.process('- ' + logger.__get_date() + ' - ' + s))

    def info(s):
        logging.info(printer.info('- ' + logger.__get_date() + ' - ' + s))

    def warning(s):
        logging.warning(
            printer.warning('- ' + logger.__get_date() + ' - ' + yellow(s)))

    def error(s):
        logging.error(
            printer.error('- ' + logger.__get_date() + ' - ' + red(s)))

    def critical(s):
        logging.critical(
            printer.critical(
                '- ' + logger.__get_date() + ' - ' + bold(red(s))))
