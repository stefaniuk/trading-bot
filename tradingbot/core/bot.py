import os.path
import time
from getpass import getpass
from optparse import OptionParser
from .color import *
from .logger import *
from ..configurer import Configurer
from .algorithm import *


class Bot(object):
    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "data.yml")
        self.configurer = Configurer(path)
        self.getArgvs()
        logger.setlevel(self.options.verbosity)

    def getArgvs(self):
        parser = OptionParser()
        parser.add_option("-v", "--verbosity",
                          dest="verbosity",
                          default='info',
                          help="Set the level of verbosity.",
                          action="store",
                          type="string")
        (options, args) = parser.parse_args()
        self.options = options

    def conf(self):
        if self.configurer.checkFile():
            self.configurer.read()
        else:
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
            stocks = input(printer.user_input(
                "Favourite stocks (sep by spaces): ")).split(' ')
            strategy = input(printer.user_input("Strategy: "))
            general = {'username': username, 'password': password}
            monitor = {'username': username2, 'password': password2,
                       'stocks': stocks, 'initiated': 0}
            self.configurer.config['strategy'] = {
                'strategy': strategy}
            self.configurer.config['general'] = general
            self.configurer.config['monitor'] = monitor
            self.configurer.save()

    def start(self):
        self.conf()
        self.configurer.config['logger_level'] = self.options.verbosity
        self.configurer.save()
        self.pivot = Pivot(self.configurer)
        self.pivot.start()

    def stop(self):
        self.pivot.stop()


def main():
    import sys

    bot = Bot()
    try:
        bot.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        sys.stderr.write('\r' + printer.info(red("exiting...\n")))
        bot.stop()
        sys.exit()


if __name__ == "__main__":
    main()
