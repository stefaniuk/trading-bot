# -*- coding: utf-8 -*-

"""
test
~~~~~~~~~~~~~~

This module control everything.
"""

import sys
import time
from tradingbot.core.interface import telegram

# logging
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - " +
                    "%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    tele = telegram.TeleHandler()
    logger.debug("telegram handler initiated")
    tele.listen()
    logger.debug("teleHandler listening")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("Exiting...")
        tele.stop()
