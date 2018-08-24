import requests
import json
from feedback import UserException

url = "http://192.168.1.126:9000/jsonrpc.js"

commands = {
  "PLAY": ["play"],
  "PAUSE": ["pause"],
  "POWER ON": ["power", "1"],
  "POWER OFF": ["power", "0"],
  "VOLUME UP": ["mixer","volume","+10"],
  "VOLUME DOWN": ["mixer","volume","-10"],
  "SLEEP": ["sleep","300"],
  "SLEEP SONG": ["jiveendoftracksleep"],
  "SKIP": ["playlist","index","+1"],
  "PREVIOUS": ["playlist","index","-1"]
}

player_macs = {}
cached_player = None

search_types = {
  "SONG": "track",
  "ALBUM": "album",
  "ARTIST": "contributor"
}
default_search_type = "SONG"

def _cache_player(f):
  def cached_f(details):
    global cached_player
    if (not cached_player == None) and ("room" not in details or details["room"] == "$room"):
      details["room"] = cached_player
    else:
      cached_player = details['room']
    f(details)
  return cached_f

@_cache_player
def simple_command(details):
  """Sends a simple squeezebox commands
  
  Sends one of the fixed commands to the specified squeezebox

  Args:
    details: {"room": string, "command": string}
  """
  if "room" not in details:
    raise Exception("Room not specified")
  elif "command" not in details:
    raise Exception("Command not specified")

  if details['command'] not in commands:
    raise Exception("command must be one of: " + str(commands.keys()))
  if details['room'] not in player_macs:
    raise Exception("player must be one of: " + str(player_macs.keys()))

  _make_request(player_macs[details['room']], commands[details['command']])

@_cache_player
def search_and_play(details):
  """Plays the specified music
  
  Searches for the specified music and loads it on the specified squeezebox

  Args:
    details: {"room": string, "term": string, "type": string}
      - term is the string to search for
      - type is the search mode; ie. track/album...
  """
  if "room" not in details:
    raise Exception("Room not specified")
  elif "term" not in details:
    raise Exception("Search term not specified")
  elif "type" not in details:
    raise Exception("Search type not specified")

  if details['room'] not in player_macs:
    raise Exception("player must be one of: " + str(player_macs.keys()))
  if details['term'] == "":
    raise UserException("Search term cannot be empty")
    
  if details['type'] == '$type':
    details['type'] = default_search_type
  elif details['type'] not in search_types:
    raise Exception("Search type must be one of: " + str(search_types.keys()))
    
  result = _make_request(player_macs[details['room']], ["search", 0, 1, "term:" + details["term"]])["result"]

  type = search_types[details['type']]
  if type+'s_loop' not in result or len(result[type+'s_loop']) < 1:
    raise UserException("No " + type + " matching: " + details["term"])

  entity = result[type+'s_loop'][0]
  entity_id = entity[type+'_id']
  entity_id_type = 'artist_id:' if details['type'] == "ARTIST" else type+"_id:"
  _make_request(player_macs[details['room']], ["playlistcontrol", "cmd:load", entity_id_type + str(entity_id)])

  
@_cache_player
def set_volume(details):
  """Sets volume at specified level
  
  Sets the volume of the specified squeezebox at the specified level

  Args:
    details: {"room": string, "percent": string}
  """
  if "room" not in details:
    raise Exception("Room not specified")
  elif "percent" not in details:
    raise Exception("Percentage not specified")
  
  if details['room'] not in player_macs:
    raise Exception("player must be one of: " + str(player_macs.keys()))
  
  if type(details['percent']) == int:
    percent = details['percent']
  else:
    try:
      percent = int(details['percent'])
    except:
      raise Exception("Percentage must be a integer")
      
  if percent < 0 or percent > 100:
    raise Exception("Percentage must be a integer")
    
  _make_request(player_macs[details['room']], ["mixer","volume",str(percent)])

@_cache_player
def play_radio4(details):
  """Plays BBC Radio 4
  
  Plays BBC radio 4 via the favourite

  Args:
    details: {"room": string}
  """
  if "room" not in details:
    raise Exception("Room not specified")
  url = "http://192.168.1.126:9000/plugins/Favorites/index.html?action=play&index=9&player="
  requests.get(url+player_macs[details['room']])

def _populate_player_macs():
  global player_macs
  player_macs = {}
  count = int(_make_request('-', ["player","count", "?"])['result']['_count'])
  for player in _make_request('-', ["players","0", count])['result']['players_loop']:
    # get rid of the thing in brackets at the end
    name = player['name'].split("(", 1)[0][:-1]
    player_macs[name] = player['playerid']

  
def _make_request(player, command):
  payload = {'method': 'slim.request', 'params': [player, command]}
  req = requests.post(url, json=payload)
  return json.loads(req.content.decode("ascii"))

if __name__ == "__main__":
  # search_and_play({"room": "UPSTAIRS BATHROOM", "term": "hall of the mountain"})
  search_and_play({"room": "SAMS BEDROOM", "type": "ARTIST", "term": "queen"})


_populate_player_macs()
