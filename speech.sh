#!/bin/bash
say_google() { 
  mpg321 -q \
  "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$*&tl=en";
}
say_pico() {
  pico2wave --wave /tmp/response.wav -l en-US "$*" \
  && aplay -q /tmp/response.wav \
  && rm /tmp/response.wav
}
say_festival() {
  flite -voice slt -t "$*"
}
say_festival $*
