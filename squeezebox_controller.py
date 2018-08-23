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

player_macs = {}

search_types = {
  "SONG": "track",
  "ALBUM": "album",
  "ARTIST": "contributor"
}
default_search_type = "SONG"

def cachePlayer(f):
  player = None
  def cached_f(details):
    nonlocal player
    if (not player == None) and ("room" not in details or details["room"] == "$room"):
      details["room"] = player
    else:
      player = details['room']
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
  if details['room'] not in player_macs:
    raise Exception("player must be one of: " + str(player_macs.keys()))

  make_request(player_macs[details['room']], commands[details['command']])

@cachePlayer
def searchAndPlay(details):
  if "room" not in details:
    raise Exception("Room not specified")
  elif "term" not in details:
    raise Exception("Search term not specified")
  elif "type" not in details:
    raise Exception("Search type not specified")

  if details['room'] not in player_macs:
    raise Exception("player must be one of: " + str(player_macs.keys()))
  if details['term'] == "":
    raise Exception("Search term cannot be empty")
    
  if details['type'] == '$type':
    details['type'] = default_search_type
  elif details['type'] not in search_types:
    raise Exception("Search type must be one of: " + str(search_types.keys()))
    
  result = make_request(player_macs[details['room']], ["search", 0, 1, "term:" + details["term"]])["result"]

  type = search_types[details['type']]
  if type+'s_loop' not in result or len(result[type+'s_loop']) < 1:
    print("No " + type + " matching: " + details["term"])
    return

  entity = result[type+'s_loop'][0]
  entity_id = entity[type+'_id']
  entity_id_type = 'artist_id:' if details['type'] == "ARTIST" else type+"_id:"
  make_request(player_macs[details['room']], ["playlistcontrol", "cmd:load", entity_id_type + str(entity_id)])

  
@cachePlayer
def setVolume(details):
  if "room" not in details:
    raise Exception("Room not specified")
  elif "percent" not in details:
    raise Exception("Percentage not specified")
  
  if details['room'] not in player_macs:
    raise Exception("player must be one of: " + str(player_macs.keys()))
  
  try:
    percent = int(details['percent'])
  except:
    raise Exception("Percentage must be a integer")
    
  if percent < 0 or percent > 100:
    raise Exception("Percentage must be a integer")
    
  make_request(player_macs[details['room']], ["mixer","volume",str(percent)])


def populate_player_macs():
  player_macs = {}
  count = int(make_request('-', ["player","count", "?"])['result']['_count'])
  for player in make_request('-', ["players","0", count])['result']['players_loop']:
    # get rid of the thing in brackets at the end
    name = player['name'].split("(", 1)[0][-1]
    player_macs[name] = player['playerid']

  
def make_request(player, command):
  payload = {'method': 'slim.request', 'params': [player, command]}
  req = requests.post(url, json=payload)
  return json.loads(req.content.decode("ascii"))

if __name__ == "__main__":
  # searchAndPlay({"room": "UPSTAIRS BATHROOM", "term": "hall of the mountain"})
  searchAndPlay({"room": "SAMS BEDROOM", "type": "ARTIST", "term": "queen"})


populate_player_macs()
