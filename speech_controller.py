
from subprocess import call,DEVNULL
from sys import argv
import os

speech_path = os.path.dirname(os.path.realpath(__file__)) + '/speech.sh'

def speak(text):
  call([speech_path, text], stdout=DEVNULL, stderr=DEVNULL)
  
if __name__ == "__main__":
  if len(argv) > 1:
    speak(argv[1])
  else:
    speak("Stop that please")