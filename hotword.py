#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import argparse
import json
import os.path
import pathlib2 as pathlib

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

import assistant_squeezebox_controller as squeezebox

import sys
import datetime

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""


class Logger(object):
    def __init__(self, filename):
        self.filename = filename

    def write(self, message):
        with open(self.filename, "a") as f:
          f.write(message)

    def flush(self):
        pass

def log(x):
  now = datetime.datetime.now().strftime('%F_%X')
  x['time'] = now
  print(x)

def process_event(event):
    """
    Args:
        event(event.Event): The current event to process.
    """
    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in event.actions:
            log({'type': 'device action', 'command': command, 'params': params})
            try:
              if command == "com.example.commands.SqueezeBoxCommand":
                  squeeze_controller.simple_command(params)
              elif command == "com.example.commands.SqueezeBoxQuery":
                  ans = str(squeeze_controller.simple_query(params))
                  speak(ans)
                  log({'type': 'squeezebox response', 'message': ans})
              elif command == "com.example.commands.SqueezeBoxSearch":
                  ans = str(squeeze_controller.search_and_play(params))
                  speak(ans)
                  log({'type': 'squeezebox response', 'message': ans})
              elif command == "com.example.commands.SqueezeBoxSpotifySearch":
                  ans = str(squeeze_controller.spotify_search_and_play(params))
                  speak(ans)
                  log({'type': 'squeezebox response', 'message': ans})
              elif command == "com.example.commands.SqueezeBoxVolume":
                  squeeze_controller.set_volume(params)
              elif command == "com.example.commands.SqueezeBoxSendMusic":
                  squeeze_controller.send_music(params)
              elif command == "com.example.commands.SqueezeBoxSync":
                  squeeze_controller.sync_player(params)
              elif command == "com.example.commands.SqueezeBoxRadio4":
                  squeeze_controller.play_radio4(params)
            except squeezebox.UserException as e:
              e = str(e)
              speak(e)
              log({'type': 'squeezebox response', 'message': e})
            except Exception as e:
              e = str(e)
              speak(e)
              log({'type': 'exception', 'message': e})
              
    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
      log({'type': 'speech', 'text': event.args['text']})
    
    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
      log({'type': 'listening'})
      squeeze_controller.quiet()

    elif event.type == EventType.ON_END_OF_UTTERANCE:
      squeeze_controller.return_volume()

    elif event.type == EventType.ON_RENDER_RESPONSE:
      log({'type': 'google response', 'text': event.args['text']})

def setup_controllers(ip_address, nearest_squeezebox):
  global squeeze_controller
  squeeze_controller = squeezebox.AssistantSqueezeBoxController(ip_address, 9000, main_squeezebox=nearest_squeezebox)

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--device-model-id', '--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=False,
                        help='the device model ID registered with Google')
    parser.add_argument('--project-id', '--project_id', type=str,
                        metavar='PROJECT_ID', required=False,
                        help='the project ID used to register this device')
    parser.add_argument('--device-config', type=str,
                        metavar='DEVICE_CONFIG_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'googlesamples-assistant',
                            'device_config_library.json'
                        ),
                        help='path to store and read device configuration')
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='path to store and read OAuth2 credentials')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + Assistant.__version_str__())

    parser.add_argument('--ip_address', type=str, required=True,
                        help='ip address of squeeze server')
    parser.add_argument('--logfile', type=str, required=False,
                        help='file to write the log to')
    parser.add_argument('--nearest_squeezebox', type=str, required=False,
                        help='squeezebox to mute when speaking')

    args = parser.parse_args()

    if args.logfile:
        sys.stdout = sys.stderr = Logger(args.logfile)

    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    device_model_id = None
    last_device_id = None
    try:
        with open(args.device_config) as f:
            device_config = json.load(f)
            device_model_id = device_config['model_id']
            last_device_id = device_config.get('last_device_id', None)
    except FileNotFoundError:
        pass

    if not args.device_model_id and not device_model_id:
        raise Exception('Missing --device-model-id option')

    # Re-register if "device_model_id" is given by the user and it differs
    # from what we previously registered with.
    should_register = (
        args.device_model_id and args.device_model_id != device_model_id)

    device_model_id = args.device_model_id or device_model_id

    with Assistant(credentials, device_model_id) as assistant:
        global speak
        speak = lambda x: assistant.send_text_query("repeat after me " + x)

        events = assistant.start()

        device_id = assistant.device_id
        log({
          "type": "starting up",
          "device_model_id": device_model_id,
          "device_id": device_id
        })

        # Re-register if "device_id" is different from the last "device_id":
        if should_register or (device_id != last_device_id):
            if args.project_id:
                register_device(args.project_id, credentials,
                                device_model_id, device_id)
                pathlib.Path(os.path.dirname(args.device_config)).mkdir(
                    exist_ok=True)
                with open(args.device_config, 'w') as f:
                    json.dump({
                        'last_device_id': device_id,
                        'model_id': device_model_id,
                    }, f)
            else:
                print(WARNING_NOT_REGISTERED)

        setup_controllers(args.ip_address, args.nearest_squeezebox)

        for event in events:
            process_event(event)


if __name__ == '__main__':
    main()
