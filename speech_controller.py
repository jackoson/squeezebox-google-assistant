
from subprocess import call,DEVNULL
from sys import argv

def speak(text):
  call(['./speech.sh', text], stdout=DEVNULL, stderr=DEVNULL)
  
if __name__ == "__main__":
  if len(argv) > 1:
    speak(argv[1])
  else:
    speak("Stop that please")