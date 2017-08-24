from tradingAPI import API
from getpass import getpass

from .color import *
from .config import Configurer

class Bot(object):
    def __init__(self):
        self.config = Configurer("data.ini")

    def conf(self):
        print(bold(blue("------ CONFIG ------")))
        print("Add your credentials")
        print("for Trading212")
        print(bold(blue("--------------------")))
        username = input(bold(yellow("Username: ")))
        password = getpass(bold(yellow("Password: ")))
        print(bold(blue("--------------------")))
        print("Add your information")
        print("for a monitoring")
        print("account")
        print(bold(blue("--------------------")))
        username2 = input(bold(yellow("Username: ")))
        password2 = getpass(bold(yellow("Password: ")))
        stocks = input(bold(yellow("Favourite stocks (sep by spaces): "))).split(' ')
        self.config.addLogin(username, password)
        self.config.addMonitor(username2, password2, stocks)

    def checkConf(self):
        if not self.config.checkFile():
            self.conf()
        else:
            self.config.read()
        
    def start(self):
        self.api = API()