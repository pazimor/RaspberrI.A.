sudo apt-get update && sudo apt-get upgrade

## pip

sudo apt-get install python-pip python3-pip -y
sudo pip install --upgrade pip
sudo pip install gtts

## swig
sudo apt-get install libpcre3-dev -y
wget -O swig-3.0.12.tar.gz https://downloads.sourceforge.net/project/swig/swig/swig-3.0.12/swig-3.0.12.tar.gz?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fswig%2Ffiles%2Fswig%2Fswig-3.0.12%2Fswig-3.0.12.tar.gz%2Fdownload&ts=1486782132&use_mirror=superb-sea2
tar xf swig-3.0.12.tar.gz
cd swig-3.0.12
./configure --prefix=/usr
make -j 4
sudo make install

## other
sudo apt-get install python-pyaudio python3-pyaudio -y
sudo apt-get install sox libatlas-base-dev git -y
sudo apt install python3-dev -y

## library 
git clone https://github.com/Kitt-AI/snowboy.git
