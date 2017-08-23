from tradingAPI import API
from getpass import getpass

from color import *
from config import Configurer

class Bot(object):
    def __init__(self):
        self.api = API()
        self.config = Configurer("data.ini")

    def conf(self):
        print(bold(blue("CONFIG")))
        print("--------------------")
        print("Add your credentials\n\
               for Trading212")
        username = input(bold(yellow("Username: ")))
        password = getpass(bold(yellow("Password: ")))
        self.config.addLogin(username, password)

    def checkConf(self):
        if self.config.checkFile():
            self.conf()
        else:
            self.config.read()