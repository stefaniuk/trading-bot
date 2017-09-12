FROM phusion/baseimage:0.9.22
MAINTAINER Federico Lolli
# INIT
CMD ["/sbin/my_init"]
RUN apt-get -qq update
RUN apt-get -y install wget
RUN apt-get -y install vim nano
################## BEGIN INSTALLATION ######################
RUN apt-get -y install xvfb
RUN apt-get -y install firefox
RUN apt-get -y install python3.6
RUN apt-get -y install python3-venv
RUN apt-get -y install git
##################### INSTALLATION END #####################
##### PIP #####
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN pip install virtualenv
###############
# GECKODRIVER #
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz
RUN tar -xvzf geckodriver-v0.11.1-linux64.tar.gz
RUN rm geckodriver-v0.11.1-linux64.tar.gz
RUN chmod +x geckodriver
RUN cp geckodriver /bin/
RUN rm geckodriver*
###############
# TRADING-BOT #
WORKDIR /home
RUN git clone https://github.com/federico123579/Trading212-API.git trading-api
RUN git clone https://github.com/federico123579/trading-bot.git trading-bot
WORKDIR /home/trading-api
RUN git checkout factory
RUN pip install .
WORKDIR /home/trading-bot
RUN git checkout factory
RUN pip install wheel
RUN pip install -r dev-requirements.txt
RUN pip install .
WORKDIR /home
###############
