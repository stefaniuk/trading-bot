# -*- coding: utf-8 -*-

"""
tradingbot.core.bot
~~~~~~~~~~~~~~

This module control everything.
"""

import time
import sys
from threading import Thread
from ..core.interface import cli
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
        logging.getLogger('tradingAPI').setLevel(logging.INFO)
        # init Glob
        Glob()

    def conf(self):
        """check configuration"""
        if not Glob().mainConf.config.get("general"):
            logger.debug("configurer data.yml not found")
            cli.cli_conf()
        else:
            logger.debug("configurer data.yml found")

    def mount_comp(self, rec=Recorder, hand=Handler):
        """mount rec and hand"""
        Glob().recorder = rec()
        Glob().handler = hand()

    def start_comp(self):
        """start components"""
        rec_thread = Thread(target=Glob().recorder.start)
        hand_thread = Thread(target=Glob().handler.start)
        rec_thread.start()
        hand_thread.start()
        rec_thread.join()
        hand_thread.join()

    def init_algo(self):
        """init all algo"""
        for x, algo in enumerate(self.algo_list):
            self.algo_list[x] = algo()

    def start_algo(self):
        """start all algo"""
        for algo in self.algo_list:
            algo.start(self.options.wait)

    def start(self):
        """start the bot"""
        self.conf()  # configurate
        self.mount_comp  # initialize base components
        self.algo_list = [Ross123]
        self.init_algo()  # initialize algorithms
        self.start_comp()  # start recorder and handlers
        self.start_algo()  # start algos

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
