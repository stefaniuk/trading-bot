# -*- coding: utf-8 -*-

"""
tradingbot.core.cli
~~~~~~~~~~~~~~

This module offers cli functions.
"""
import os.path
from getpass import getpass
from optparse import OptionParser
from .color import *
from ..glob import Glob, file_path

# logging
import logging
logger = logging.getLogger('tradingbot.core.cli')


def get_argvs():
    """get args and options"""
    parser = OptionParser()
    parser.add_option("-v", "--verbosity",
                      dest="verbosity",
                      default='info',
                      help="Set the level of verbosity.",
                      action="store",
                      type="string")
    parser.add_option("-w", "--wait",
                      dest="wait",
                      default=1,
                      help="minute to attend before starting main algo.",
                      action="store",
                      type="int")
    parser.add_option("--conf",
                      dest="conf",
                      default=False,
                      help="Config only.",
                      action="store_true")
    (options, args) = parser.parse_args()
    if (options.verbosity.upper() not in
            ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']):
        raise ValueError("incorrect verbosity level")
    options.verbosity = options.verbosity.upper()
    return options


def cli_conf():
    """configurate"""
    """start the guided configuration in cli"""
    print(printer.header("config"))
    print("Add your credentials")
    print("for Trading212")
    print(bold(blue("--------------------")))
    username = input(printer.user_input("Username: "))
    password = getpass(printer.user_input("Password: "))
    print(bold(blue("--------------------")))
    print("Add your information")
    print("for a monitoring")
    print("account")
    print(bold(blue("--------------------")))
    username2 = input(printer.user_input("Username: "))
    password2 = getpass(printer.user_input("Password: "))
    prefs = input(printer.user_input(
        "Favourite stocks (sep by spaces): "))
    stocks = []
    if prefs:
        stocks = prefs.split(' ')
    strat = input(printer.user_input("Strategy: "))
    while not os.path.isfile(os.path.join(file_path['strategy'],
                                          strat + '.yml')):
        logger.error("strategy not found")
        strat = input(printer.user_input(
            "Strategy existent (not found): "))
    general = {'username': username, 'password': password}
    monitor = {'username': username2, 'password': password2,
               'stocks': stocks, 'initiated': 0}
    Glob().mainConf.config['strategy'] = strat
    Glob().mainConf.config['general'] = general
    Glob().mainConf.config['monitor'] = monitor
    Glob().mainConf.save()
