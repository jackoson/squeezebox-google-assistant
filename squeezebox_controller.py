import requests

url = "http://192.168.1.126:9000/jsonrpc.js"

commands = {
  "PLAY": "play",
  "PAUSE": "pause"
}

players = {
  "SAMS BEDROOM": "b8:27:eb:ef:48:df"
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

  return send_command(players[details['room']], commands[details['command']])

def send_command(player, command):
  payload = {'method': 'slim.request', 'params': [player, [command]]}
  req = requests.post(url, json=payload)
  return req.status_code == 200

