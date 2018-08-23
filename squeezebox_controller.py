import requests
import json

url = "http://192.168.1.126:9000/jsonrpc.js"

commands = {
  "PLAY": ["play"],
  "PAUSE": ["pause"],
  "POWER ON": ["power", "1"],
  "POWER OFF": ["power", "0"],
  "VOLUME UP": ["mixer","volume","+10"],
  "VOLUME DOWN": ["mixer","volume","-10"],
  "SLEEP": ["sleep","300"],
  "SLEEP SONG": ["jiveendoftracksleep"]
}

players = {
  "SAMS BEDROOM": "b8:27:eb:ef:48:df",
  "KITCHEN":"00:04:20:05:b2:d8", 
  "UPSTAIRS BATHROOM":"00:04:20:12:6e:96"
}

search_types = {
  "SONG": "track",
  "ALBUM": "album",
  "ARTIST": "contributor"
}
default_search_type = "SONG"

def cachePlayer(f):
  player = None
  def cached_f(details):
    if (not player == None) and ("room" not in details or details["room"] == "$room"):
      details["room"] = player
    f(details)
  return cached_f

@cachePlayer
def simpleCommand(details):
  if "room" not in details:
    raise Exception("Room not specified")
  elif "command" not in details:
    raise Exception("Command not specified")

  if details['command'] not in commands:
    raise Exception("command must be one of: " + str(commands.keys()))
  if details['room'] not in players:
    raise Exception("player must be one of: " + str(players.keys()))

  send_command(players[details['room']], commands[details['command']])

@cachePlayer
def searchAndPlay(details):
  if "room" not in details:
    raise Exception("Room not specified")
  elif "term" not in details:
    raise Exception("Search term not specified")
  elif "type" not in details:
    raise Exception("Search type not specified")

  if details['room'] not in players:
    raise Exception("player must be one of: " + str(players.keys()))
  if details['term'] == "":
    raise Exception("Search term cannot be empty")
    
  if details['type'] == '$type':
    details['type'] = default_search_type
  elif details['type'] not in search_types:
    raise Exception("Search type must be one of: " + str(search_types.keys()))
    
  result = send_command(players[details['room']], ["search", 0, 1, "term:" + details["term"]])["result"]
  print(result)
  type = search_types[details['type']]
  if type+'s_loop' not in result or len(result[type+'s_loop']) < 1:
    print("No " + type + " matching: " + details["term"])
    return

  entity = result[type+'s_loop'][0]
  entity_id = entity[type+'_id']
  entity_id_type = 'artist_id:' if details['type'] == "ARTIST" else type+"_id:"
  send_command(players[details['room']], ["playlistcontrol", "cmd:load", entity_id_type + str(entity_id)])


def send_command(player, command):
  payload = {'method': 'slim.request', 'params': [player, command]}
  req = requests.post(url, json=payload)
  return json.loads(req.content.decode("ascii"))

if __name__ == "__main__":
  # searchAndPlay({"room": "UPSTAIRS BATHROOM", "term": "hall of the mountain"})
  searchAndPlay({"room": "SAMS BEDROOM", "type": "ARTIST", "term": "queen"})
