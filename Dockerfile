FROM phusion/baseimage:0.9.22
MAINTAINER Federico Lolli
# INIT
CMD ["/sbin/my_init"]
RUN apt-get -qq update
RUN apt-get -y install wget curl
RUN apt-get -y install vim nano unzip
################## BEGIN INSTALLATION ######################
RUN apt-get -y firefox
RUN apt-get -y install xvfb
# GECKODRIVER #
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz
RUN tar -xvzf geckodriver-v0.11.1-linux64.tar.gz
RUN rm geckodriver-v0.11.1-linux64.tar.gz
RUN chmod +x geckodriver
RUN cp geckodriver /bin/
RUN rm geckodriver*
###############
## PYTHON3.6 ##
RUN apt-get -y install build-essential checkinstall
RUN apt-get -y install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
RUN apt-get -y install python3-venv
WORKDIR /usr/src
RUN wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz
RUN tar xzf Python-3.6.2.tgz
RUN rm Python-3.6.2.tgz
WORKDIR /usr/src/Python-3.6.2
RUN ./configure
RUN make altinstall
WORKDIR /home
###############
RUN apt-get -y install git
##################### INSTALLATION END #####################
##### PIP #####
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN pip3.6 install virtualenv
###############
# TRADING-BOT #
WORKDIR /home
RUN git clone https://github.com/federico123579/Trading212-API.git trading-api
RUN git clone https://github.com/federico123579/trading-bot.git trading-bot
WORKDIR /home/trading-api
RUN git checkout testing
RUN pip3.6 install .
WORKDIR /home/trading-bot
RUN git checkout factory
RUN pip3.6 install wheel
RUN pip3.6 install -r dev-requirements.txt
RUN pip3.6 install .
WORKDIR /home
###############
