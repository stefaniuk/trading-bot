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
from ..patterns import Observer
from ..glob import Glob
from .recorder import Recorder
from .handler import Handler
from .algorithms.scalper import Scalper
from .algorithms.ross123 import Ross123
import telegram
from telegram import (KeyboardButton, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ParseMode)
from telegram.ext import Updater, CommandHandler


# logging
import logging
logger = logging.getLogger('tradingbot.bot')
telelog = logging.getLogger('tradingbot.telegram')


class Bot(object):
    def __init__(self):
        self.options = cli.get_argvs()
        verbosity = getattr(logging, self.options.verbosity)  # verbosity
        logging.getLogger('tradingbot').setLevel(verbosity)
        logging.getLogger('tradingAPI').setLevel(logging.INFO)  # CORRECT
        Glob()  # init Glob
        Glob().Bot = self
        Glob().tele = TeleHandler()
        self.state = False

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
        if self.state:
            logger.error("bot has already started")
            return
        self.conf()  # configurate
        self.mount_comp()  # initiate base components
        self.algo_list = [Ross123]
        self.init_algo()  # initiate algorithms
        self.start_comp()  # start recorder and handlers
        self.start_algo()  # start algos
        self.state = True

    def stop(self):
        """stop algos from telegram"""
        if not self.state:
            logger.error("bot has already been stopped")
            return
        Glob().recorder.stop()
        Glob().handler.stop()
        self.state = False


# Create Telegram handler
class TeleHandler(Observer):
    """class that handle telegram UI"""
    def __init__(self):
        self.token = "488447858:AAGgZgtXj4cOQ02KQntGDa6xzhEBVuyxaJk"
        self.bot = telegram.Bot(token=self.token)
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        logger.debug("TeleHandler initiated")

    def listen(self):
        """start and listen"""
        handlers = []
        handlers.append(CommandHandler('start', self.cmd_start))
        handlers.append(CommandHandler('stop', self.cmd_stop))
        handlers.append(CommandHandler('restart', self.cmd_restart))
        handlers.append(CommandHandler('update', self.cmd_update))
        handlers.append(CommandHandler('closeall', self.cmd_close_all))
        for hand in handlers:  # add all handlers
            self.dispatcher.add_handler(hand)
        self.updater.start_polling()  # start listening

    def cmd_start(self, bot, update):
        """start the bot"""
        telelog.debug("start command caught")
        self.chat_id = update.message.chat_id
        update.message.reply_text("Starting...")
        Glob().Bot.start()
        update.message.reply_text("Bot started")  # reply with text

    def cmd_stop(self, bot, update):
        """stop the bot"""
        telelog.debug("stop command caught")
        update.message.reply_text("Stopping...")
        Glob().Bot.stop()
        update.message.reply_text("Bot stopped")

    def cmd_restart(self, bot, update):
        """restart the bot"""
        telelog.debug("restart command caught")
        update.message.reply_text("Restarting...")
        Glob().Bot.stop()
        Glob().Bot.start()
        update.message.reply_text("Restarted")

    def cmd_update(self, bot, update):
        """update positions"""
        telelog.debug("update command caught")
        bot.send_chat_action(chat_id=self.chat_id, action='typing')
        Glob().handler.update()
        poss = Glob().handler.positions
        text = ""
        if not poss:
            text = "Currently, there aren't any positions opened"
        for pos in poss:
            text += ("%d *%s* - gain: *%g*\n" %
                     (pos.quantity, pos.product, pos.gain))
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    def cmd_close_all(self, bot, update):
        """close all positions"""
        telelog.debug("close_all command caught")
        update.message.reply_text("Closing all positions...")
        count = 0
        gain = 0
        for pos in Glob().handler.positions:
            pos.close()
            count += 1
            gain += pos.gain
        update.message.reply_text("Closed %d positions with gain of *%g*" %
                                  (count, gain), parse_mode=ParseMode.MARKDOWN)

    def stop(self):
        """stop listening"""
        self.updater.stop()

    def notify(self, observable, event, data):
        """catch the event"""
        if event == 'auto-transaction':
            if data['mode'] == 'buy':
                mode = 'Bought'
            else:
                mode = 'Sold'
            text = ("%s *%s* with auto margin of %g" +
                    " and a stop limit of %g and %g") % (
                        mode, data['product'], data['margin'],
                        data['stop_limit'][0],
                        data['stop_limit'][1])
        if event == 'close':
            text = ("Closed %s position with a gain of *%g*" %
                    (data['product'], data['gain']))
        self.bot.send_message(chat_id=self.chat_id, text=text,
                              parse_mode=ParseMode.MARKDOWN)


# Create a button menu to show in Telegram messages
def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)

    return menu


# Custom keyboards
def keyboard_confirm():
    buttons = [
        KeyboardButton("YES"),
        KeyboardButton("NO")
    ]

    return ReplyKeyboardMarkup(build_menu(buttons, n_cols=2))


def main():
    bot = Bot()
    # if config option
    if bot.options.conf:
        cli.cli_conf()
        print("config saved")
        sys.exit()
    Glob().tele.listen()
    try:
        while True:
            time.sleep(60)
    except Exception as e:
        logger.error(e)
        raise
    except KeyboardInterrupt as e:
        sys.stderr.write('\r' + "exiting...\n")
        bot.stop()
        Glob().tele.stop()
        sys.exit()


if __name__ == "__main__":
    main()
