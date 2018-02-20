sudo apt-get update && sudo apt-get upgrade

## pip
sudo apt-get install python-pip python3-pip -y
sudo pip3 install --upgrade pip
sudo pip3 install gtts

## swig
sudo dpkg -i swig/swig3.deb
sudo dpkg -i swig/swig3.0.10.deb

## other
sudo apt-get install python-pyaudio python3-pyaudio sox libatlas-base-dev git python3-dev -y

## library
git clone https://github.com/Kitt-AI/snowboy.git
make -C ~/RaspberrI.A./snowboy/swig/Python3
make -C ~/RaspberrI.A./snowboy/swig/Python

## move into project
cp ~/RaspberrI.A./snowboy/swig/Python3/_snowboydetect.so ~/RaspberrI.A./IA/
cp ~/RaspberrI.A./snowboy/swig/Python3/snowboydetect.py ~/RaspberrI.A./IA/
rm -rf ~/RaspberrI.A./snowboy
