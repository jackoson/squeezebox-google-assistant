#!/bin/bash
say() { 
  mplayer -ao alsa -really-quiet -noconsolecontrols -softvol -volume 20\
  "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$*&tl=en";
}
say $*
