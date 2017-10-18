# -*- coding: utf-8 -*-

"""
tradingbot.core.bot
~~~~~~~~~~~~~~

This module control everything.
"""

import time
import sys
from ..core import cli
from ..glob import Glob
from .recorder import Recorder
from .handler import Handler
from .algorithms.scalper import Scalper

# logging
import logging
logger = logging.getLogger('tradingbot.bot')


class Bot(object):
    def __init__(self):
        self.options = cli.get_argvs()
        # verbosity
        verbosity = getattr(logging, self.options.verbosity)
        logging.getLogger('tradingbot').setLevel(verbosity)
        logging.getLogger('tradingAPI').setLevel(verbosity)
        # init Glob
        Glob()

    def conf(self):
        """check configuration"""
        if not Glob().mainConf.config.get("general"):
            logger.debug("configurer data.yml not found")
            cli.cli_conf()
        else:
            logger.debug("configurer data.yml found")
        # init strategy config
        Glob().init_strategy(Glob().collection['main']['strategy'])

    def start(self):
        """start the bot"""
        self.conf()
        # initialize base components
        Glob().recorder = Recorder()
        Glob().handler = Handler()
        # initialize algorithms
        self.scalper = Scalper()
        # start algos
        self.scalper.start()

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
            time.sleep(1)
    except Exception as e:
        logger.error(e)
        raise
    except KeyboardInterrupt as e:
        sys.stderr.write('\r' + "exiting...\n")
        bot.stop()
        sys.exit()


if __name__ == "__main__":
    main()
