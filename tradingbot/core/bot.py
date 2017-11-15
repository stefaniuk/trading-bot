# -*- coding: utf-8 -*-

"""
tradingbot.core.bot
~~~~~~~~~~~~~~

This module control everything.
"""

import time
import sys
from threading import Thread
from ..core import cli
from ..glob import Glob
from .recorder import Recorder
from .handler import Handler
from .algorithms.scalper import Scalper
from .algorithms.ross123 import Ross123

# logging
import logging
logger = logging.getLogger('tradingbot.bot')


class Bot(object):
    def __init__(self):
        self.options = cli.get_argvs()
        # verbosity
        verbosity = getattr(logging, self.options.verbosity)
        logging.getLogger('tradingbot').setLevel(verbosity)
        # CORRECT
        logging.getLogger('tradingAPI').setLevel(logging.WARNING)
        # init Glob
        Glob()

    def conf(self):
        """check configuration"""
        if not Glob().mainConf.config.get("general"):
            logger.debug("configurer data.yml not found")
            cli.cli_conf()
        else:
            logger.debug("configurer data.yml found")

    def start(self):
        """start the bot"""
        self.conf()
        # initialize base components
        Glob().recorder = Recorder()
        Glob().handler = Handler()
        # initialize algorithms
        # scalper = Scalper()
        ross123 = Ross123()
        # start recorder and handlers
        rec_thread = Thread(target=Glob().recorder.start)
        hand_thread = Thread(target=Glob().handler.start)
        rec_thread.start()
        hand_thread.start()
        rec_thread.join()
        time.sleep(65)
        hand_thread.join()
        # start algos
        # scalper.start(self.options.wait)
        ross123.start(self.options.wait)

    def stop(self):
        """stop the bot"""
        Glob().recorder.stop()
        Glob().handler.stop()


def main():
    bot = Bot()
    if bot.options.conf:
        cli.cli_conf()
        print("config saved")
        sys.exit()
    try:
        bot.start()
        while True:
            time.sleep(60)
    except Exception as e:
        logger.error(e)
        raise
    except KeyboardInterrupt as e:
        sys.stderr.write('\r' + "exiting...\n")
        bot.stop()
        sys.exit()


if __name__ == "__main__":
    main()
