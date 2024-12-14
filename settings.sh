apt-get update -y
apt-get upgrade -y
apt-get install git -y
apt-get install git-flow -y
apt-get install python3-pip -y
apt-get install uvicorn -y


# Selenium 세팅
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y

wget https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip
unzip chromedriver_linux64.zip


