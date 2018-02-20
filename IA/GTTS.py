from gtts import gTTS
import os
import sys

if len(sys.argv) < 1:
    sys.exit(-84)
tts = gTTS(sys.argv[1], "fr", False)
tts.save("speak.mp3")
os.system ("mpg321 speak.mp3")
os.remove("speak.mp3")
