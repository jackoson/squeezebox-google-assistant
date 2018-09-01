import requests
import json
from functools import wraps
from feedback import UserException

end_point_url = "http://192.168.1.126:9000/jsonrpc.js"

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
  "PREVIOUS": ["playlist","index","-1"],
  "UNSYNC": ["sync","-"],
  "SHUFFLE OFF": ["playlist","shuffle",0],
  "SHUFFLE SONGS": ["playlist","shuffle",1],
  "SHUFFLE ALBUMS": ["playlist","shuffle",2],
  "REPEAT OFF": ["playlist","repeat",0],
  "REPEAT SONG": ["playlist","repeat",1],
  "REPEAT PLAYLIST": ["playlist","repeat",2]
}

player_macs = {}
cached_player = None

search_types = {
  "SONG": "track",
  "ALBUM": "album",
  "ARTIST": "contributor"
}
default_search_type = "SONG"

queries = {
  "VOLUME": lambda info: "The volume is at %d percent"%(info['mixer volume']),
  "NOW PLAYING": lambda info: info['playlist_loop'][0]['title'] + ' by ' + info['playlist_loop'][0]['artist'] \
                      if 'playlist_loop' in info and len(info['playlist_loop']) > 0 else "Nothing is playing"
}

def _cache_player(f):
  @wraps(f)
  def cached_f(details):
    global cached_player
    if (not cached_player == None) and ("player" not in details or details["player"] == "$player"):
      details["player"] = cached_player
    else:
      cached_player = details['player']
    return f(details)
  return cached_f

@_cache_player
def simple_command(details):
  """Sends a simple squeezebox commands
  
  Sends one of the fixed commands to the specified squeezebox

  Args:
    details: {"player": string, "command": string}
  """
  if "player" not in details:
    raise Exception("Player not specified")
  elif "command" not in details:
    raise Exception("Command not specified")

  if details['command'] not in commands:
    raise Exception("command must be one of: " + str(commands.keys()))
  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))

  _make_request(player_macs[details['player']], commands[details['command']])

@_cache_player
def search_and_play(details):
  """Plays the specified music
  
  Searches for the specified music and loads it on the specified squeezebox

  Args:
    details: {"player": string, "term": string, "type": string}
      - term is the string to search for
      - type is the search mode; ie. track/album...
  """
  if "player" not in details:
    raise Exception("Player not specified")
  elif "term" not in details:
    raise Exception("Search term not specified")
  elif "type" not in details:
    raise Exception("Search type not specified")

  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))
  if details['term'] == "":
    raise UserException("Search term cannot be empty")
    
  if details['type'] == '$type':
    details['type'] = default_search_type
  elif details['type'] not in search_types:
    raise Exception("Search type must be one of: " + str(search_types.keys()))
    
  result = _make_request(player_macs[details['player']], ["search", 0, 1, "term:" + details["term"]])["result"]

  type = search_types[details['type']]
  if type+'s_loop' not in result or len(result[type+'s_loop']) < 1:
    raise UserException("No " + type + " matching: " + details["term"])

  entity = result[type+'s_loop'][0]
  title = entity[type]
  entity_id = entity[type+'_id']
  entity_id_type = 'artist_id:' if details['type'] == "ARTIST" else type+"_id:"
  _make_request(player_macs[details['player']], ["playlistcontrol", "cmd:load", entity_id_type + str(entity_id)])
  return "Playing %s"%title

@_cache_player
def spotify_search_and_play(details):
  """Plays the specified music on spotify
  
  Searches for the specified music on spotify and loads it on the specified squeezebox

  Args:
    details: {"player": string, "term": string, "type": string}
      - term is the string to search for
      - type is the search mode; ie. track/album...
  """
  if "player" not in details:
    raise Exception("Player not specified")
  elif "term" not in details:
    raise Exception("Search term not specified")
  elif "type" not in details:
    raise Exception("Search type not specified")

  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))
  if details['term'] == "":
    raise UserException("Search term cannot be empty")
    
  if details['type'] == '$type':
    details['type'] = default_search_type
  elif details['type'] not in search_types:
    raise Exception("Search type must be one of: " + str(search_types.keys()))
    
  search_type_num = {
    "SONG": ".2",
    "ALBUM": ".1",
    "ARTIST": ".0"
  }
    
  item_id = "8_" + details["term"] + search_type_num[details['type']]
  command = ["spotify","items","0","1", "item_id:" + item_id, "menu:spotify"]
  result = _make_request(player_macs[details['player']], command)["result"]
  if result["count"] == 0:
    raise UserException("No " + type + " matching: " + details["term"] + "on spotify")
  
  song = result["item_loop"][0]
  uri = song["actions"]["play"]["params"]["uri"]
  title = song["text"]
  
  _make_request(player_macs[details['player']], ["spotifyplcmd", "uri:" + uri, "cmd:load"])
  return "Playing %s"%title
  

@_cache_player
def set_volume(details):
  """Sets volume at specified level
  
  Sets the volume of the specified squeezebox at the specified level

  Args:
    details: {"player": string, "percent": string}
  """
  if "player" not in details:
    raise Exception("Player not specified")
  elif "percent" not in details:
    raise Exception("Percentage not specified")
  
  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))
  
  if type(details['percent']) == int:
    percent = details['percent']
  else:
    try:
      percent = int(details['percent'])
    except:
      raise Exception("Percentage must be a integer")
      
  if percent < 0 or percent > 100:
    raise Exception("Percentage must be a integer")
    
  _make_request(player_macs[details['player']], ["mixer","volume",str(percent)])

@_cache_player
def send_music(details):
  """Sends music from one squeezebox to another
  
  Sends whatever is playing on the source to the destination squeezebox

  Args:
    details: {"player": string, "other": string, "direction": string}
  """
  if "player" not in details:
    raise Exception("Player not specified")
  if "other" not in details:
    raise Exception("Other player not specified")
  elif "direction" not in details:
    raise Exception("Direction not specified")
  
  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))
  if details['other'] not in player_macs:
    raise Exception("other player must be one of: " + str(player_macs.keys()))
  
  if details['direction'] == 'TO':
    source = player_macs[details['player']]
    dest = player_macs[details['other']]
  elif details['direction'] == 'FROM':
    source = player_macs[details['other']]
    dest = player_macs[details['player']]
  else:
    raise Exception('direction must be either "from" or "to".')
    
  _make_request(player_macs[details['player']], ["switchplayer","from:" + source,"to:" + dest])
 
@_cache_player
def sync_player(details):
  """Sends music from one squeezebox to another
  
  Sends whatever is playing on the source to the destination squeezebox

  Args:
    details: {"player": string, "other": string, "direction": string}
  """
  if "player" not in details:
    raise Exception("Player not specified")
  if "other" not in details:
    raise Exception("Other player not specified")
   
  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))
  if details['other'] not in player_macs:
    raise Exception("other player must be one of: " + str(player_macs.keys()))
  
  slave = player_macs[details['player']]
  master = player_macs[details['other']]
    
  _make_request(master, ["sync",slave])
  _make_request(slave, commands["POWER ON"])
  _make_request(master, commands["POWER ON"])
 
  
@_cache_player
def play_radio4(details):
  """Plays BBC Radio 4
  
  Plays BBC radio 4 via the favourite

  Args:
    details: {"player": string}
  """
  if "player" not in details:
    raise Exception("Player not specified")
  action_url = "http://192.168.1.126:9000/plugins/Favorites/index.html?action=play&index=9&player="
  requests.get(action_url+player_macs[details['player']])

@_cache_player
def simple_query(details):
  """Performs a simple query on a squeezebox 
  
  Performs one of the fixed queries on the specified squeezebox

  Args:
    details: {"player": string, "query": string}
  """
  if "player" not in details:
    raise Exception("Player not specified")
  elif "query" not in details:
    raise Exception("Query not specified")

  if details['query'] not in queries:
    raise Exception("Query must be one of: " + str(queries.keys()))
  if details['player'] not in player_macs:
    raise Exception("player must be one of: " + ", ".join(player_macs.keys()))

  player_info = _get_player_info(player_macs[details['player']])
  
  return queries[details['query']](player_info)
  
def _populate_player_macs():
  global player_macs
  player_macs = {}
  count = int(_make_request('-', ["player","count", "?"])['result']['_count'])
  for player in _make_request('-', ["players","0", count])['result']['players_loop']:
    # get rid of the thing in brackets at the end
    name = player['name'].split("(", 1)[0][:-1]
    player_macs[name] = player['playerid']

def _get_player_info(player):
  return _make_request(player, ["status","-"])["result"]
  
def _make_request(player, command):
  payload = {'method': 'slim.request', 'params': [player, command]}
  req = requests.post(end_point_url, json=payload)
  return json.loads(req.content.decode("utf-8"))

_populate_player_macs()

if __name__ == "__main__":
  # search_and_play({"player": "UPSTAIRS BATHROOM", "term": "hall of the mountain"})
  # search_and_play({"player": "SAMS BEDROOM", "type": "ARTIST", "term": "queen"})
  print(simple_query({"player": "Sam's Bedroom", "query": "NOW PLAYING"}))
  


