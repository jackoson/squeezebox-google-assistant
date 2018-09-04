# squeezebox-voice-assistant

Squeezebox Voice Assistant using Google assistant SDK.

When installed on a Raspberry Pi with a speaker and mic it can interact with your local SqueezeServer to control your squeezeboxes with your voice.

-----Only works locally - no external access------

To set up as own project follow the instructions on googl's [help page](https://developers.google.com/assistant/sdk/guides/library/python/embed/setup)

Then clone this repository on to Pi
git clone https://github.com/jackoson/squeezebox-google-assistant
and run 
cd squeezebox-google-assistant
python hotword.py --project_id $project_id --device_model_id $device_model_id --ip_address <ip address of SqueezeServer>

Uses [squeezebox-controller](https://github.com/jackoson/squeezebox-controller) to interface with the SqueezeServer.

