
from subprocess import call

def speak(text):
  call(['./speech.sh', text])