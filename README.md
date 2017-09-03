# TradingBot
> Trade bot with Trading212 api.

A trade bot for investing in trading212.com broker service.

## Getting started

### General

Just install it with pip.

```shell
sudo apt-get install xvfb
pip install tradingbot
```
### MacOS

Install [XQuartz](https://www.xquartz.org).

```shell
brew cask install xquarts
```

### Linux

```shell
sudo apt-get install xvfb
sudo apt-get install firefox
```

## Developing
### Built With

- python _v3.6_
- trading212api _v0.1b3_

### Prerequisites

- Python3.6
- firefox
- geckodriver
- xvfb

### Setting up Dev

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/federico123579/TradingBot.git
sudo apt-get install xvfb
cd TradingBot/
python3.6 -m venv env
. env/bin/activate
pip install .
```

#### Docker

Build a container and run it.

```shell
docker build -t tradingbot .
docker run --name tradingbot_instance -it tradingbot
```

## Versioning

The Semantic Versioning is used in this repository in this format:

    [major].[minor].[patch]-{status}

* **major** indicates incopatible changes
* **minor** indicates new features
* **patch** indicates bug fixies
* **status** show the status (alpha, beta, rc, etc.)

for more information see [Semantic Versioning](http://semver.org/)

## Licensing

This software is under the MIT license.
