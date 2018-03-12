#!/usr/bin/python3

import snowboydecoder
import sys
import signal
import os
import string

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

#= start we have to load all models here
#
said = []
script = []
Hotword = []

def storeWords(word):
    said.append(word)

def getCallbackArray(array):
    callbacks = []
    for i in array:
        callbacks.append(lambda: storeWords(i))
    return callbacks

def getVocabulary(path):
    files = [f.split(".")[0] for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f.find(".pmdl") != -1)]
    print(files)
    return files

def getCommande(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files

def getFolders(path):
    files = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return files


array = getVocabulary(os.getcwd() + "/../vocabulary")
callbacks = getCallbackArray(array)
callbacks[1]()
print(said)
folders = getFolders(os.getcwd() + "/../Cmd")
for i in folders:
    commande = getCommande(os.getcwd() + "/../Cmd/" + str(i))
    if commande[0] == "script.sh":
        script.append(os.getcwd() + "/../Cmd/" + str(i) + "/" + commande[0])
    if commande[1] == "sentence":
        Hotword.append(os.getcwd() + "/../Cmd/" + str(i) + "/" + commande[1])
print(script)
print(Hotword)

print("work in progress")
sys.exit(-1)

models = sys.argv[1:]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


sensitivity = [0.5]*len(models)
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)

# our create callback
callbacks = [lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING),
             lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)]
print('IA started')

# main loop (size callback == size models)
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
