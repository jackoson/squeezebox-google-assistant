import requests
import json

url = "http://192.168.1.126:9000/jsonrpc.js"

commands = {
  "PLAY": ["play"],
  "PAUSE": ["pause"],
  "POWER ON": ["power", "1"],
  "POWER OFF": ["power", "0"],
  "VOLUME UP": ["mixer","volume","2"],
  "VOLUME DOWN": ["mixer","volume","-2"],
  "SLEEP": ["sleep","300"],
  "SLEEP SONG": ["jiveendoftracksleep"]
}

players = {
  "SAMS BEDROOM": "b8:27:eb:ef:48:df",
  "KITCHEN":"00:04:20:05:b2:d8", 
  "UPSTAIRS BATHROOM":"00:04:20:12:6e:96"
}

def sendSqueezeBoxCommand(details):
  if "room" not in details:
    raise Exception("Room not specified")
  elif "command" not in details:
    raise Exception("Command not specified")

  if details['command'] not in commands:
    raise Exception("command must be one of: " + str(commands.keys()))
  if details['room'] not in players:
    raise Exception("player must be one of: " + str(players.keys()))

  send_command(players[details['room']], commands[details['command']])


def squeezeboxSearchAndPlay(details):
  if "room" not in details:
    raise Exception("Room not specified")
  elif "term" not in details:
    raise Exception("Search term not specified")

  if details['room'] not in players:
    raise Exception("player must be one of: " + str(players.keys()))
  if details['term'] == "":
    raise Exception("Search term cannot be empty")

  result = send_command(players[details['room']], ["search", 0, 1, "term:" + details["term"]])["result"]

  if "tracks_loop" not in result:
    raise Exception("No tracks matching: " + details["term"])

  track = result["tracks_loop"][0]
  send_command(players[details['room']], ["playlistcontrol", "track_id:" + str(track["track_id"]), "cmd:load"])


def send_command(player, command):
  payload = {'method': 'slim.request', 'params': [player, command]}
  req = requests.post(url, json=payload)
  return json.loads(req.content.decode("ascii"))

if __name__ == "__main__":
  # squeezeboxSearchAndPlay({"room": "UPSTAIRS BATHROOM", "term": "hall of the mountain"})
  squeezeboxSearchAndPlay({"room": "KITCHEN", "term": "Final Countdown"})
