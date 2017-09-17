wget 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
dpkg -i google-chrome-stable_current_amd64.deb
apt-get install -y -f
dpkg -i google-chrome-stable_current_amd64.deb
wget "http://chromedriver.storage.googleapis.com/2.30/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/chromedriver
rm chromedriver_linux64.zip
