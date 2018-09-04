# squeezebox-voice-assistant

Squeezebox Voice Assistant using Google assistant SDK.

When installed on a Raspberry Pi with a speaker and mic it can interact with your local SqueezeServer to control your squeezeboxes with your voice.

-----Only works locally - no external access-----

Voice actions only work on devices with this library installed - not on all your other google assistant devices; ie. phones

To set up, you have to follow the instructions on google's [help page](https://developers.google.com/assistant/sdk/guides/library/python/embed/setup) to create your own project.

Then...
1) clone this repository on to Pi
```bash
git clone https://github.com/jackoson/squeezebox-google-assistant
cd squeezebox-google-assistant
```

2) Add your players to the actions.json

Under _types_ find the type with _name: $Player_. In the _entities_ list, add an object for each squeezebox.
```
{
  ...
  "types": [
    ...
    {
      "name": "$Player",
      "entities": [
          {
              "key": "<player name on squeeze server>",
              "synonyms": [
                  "what you call the player"
              ]
          }
      ]
    },
    ...
  ],
  ...
}
```

3) download gactions tool
```bash
wget https://dl.google.com/gactions/updates/bin/linux/arm/gactions
chmod +x gactions
```

4) submit squeezebox action schema to google ([further tutorial](https://developers.google.com/assistant/sdk/guides/library/python/extend/custom-actions))
```bash
./gactions update --action_package actions.json --project <project_id>
./gactions test --action_package actions.json --project <project_id>
```

5) install requirements
```bash
python -m pip install -r requirements.txt
```

6) and run 
```bash
python hotword.py --project_id <project_id> --device_model_id <device_model_id> --ip_address <ip address of SqueezeServer>
```
Uses [squeezebox-controller](https://github.com/jackoson/squeezebox-controller) to interface with the SqueezeServer.

