
import socket

appliance_codes = {
  "DOWNSTAIRS BATHROOM MAIN LIGHTS"     : 8,
  "DOWNSTAIRS BATHROOM FAN"             : 23,
  "CUPBOARD LIGHTS"                     : 26,
  "LOUNGE LIGHTS"                       : 29,
  "KITCHEN MAIN LIGHTS"                 : 34,
  "KITCHEN CUPBOARD LIGHTS"             : 37,
  "HALL LIGHTS"                         : 40,
  "LANDING LIGHTS"                      : 44,
  "BEDROOM LAMP"                        : 48,
  "UTILITY ROOM LIGHTS"                 : 51,
  "UPSTAIRS BATHROOM MAIN LIGHTS"       : 58,
  "UPSTAIRS BATHROOM MIRROR LIGHTS"     : 61,
  "UPSTAIRS BATHROOM FAN"               : 72,
  "TOILET LIGHTS"                       : 87,
  "DOWNSTAIRS BATHROOM MIRROR LIGHTS"   : 145,
  
  "ALL LIGHTS"                          : 5,
  "FRONT LIGHTS"                        : 6,
  "BACK LIGHTS"                         : 7,
}

actions = {
  "HEATING HOUR"                        : lambda: _run_macro(0),
  "HEATING OFF"                         : lambda: _run_macro(1),
  "HEATING MAN ADVANCE"                 : lambda: _send_command(b'action flag set 76; __wait 500; action pe run 10; __wait 200'),
  "HOT WATER TOPUP"                     : lambda: _run_macro(2),
  "HOT WATER OFF"                       : lambda: _run_macro(4)
}

def on_off_command(details):
  """Send an on or off command to an appliance
  
  Sends the specified command to the homevision through netio interface to control the specified appliance.
  
  Args:
    details: {"appliance": string, "state": string} 
  """
  if "appliance" not in details:
    raise Exception("appliance not specified")
  elif "state" not in details:
    raise Exception("state not specified")

  if details["appliance"] not in appliance_codes.keys():
    raise Exception("appliance not supported. Must be one of: " + ",".join(appliance_codes.keys()))

  appliance_code = appliance_codes[details["appliance"]]
  
  if details["appliance"] in ["ALL LIGHTS", "FRONT LIGHTS", "BACK LIGHTS"]:
    _run_macro(appliance_code)
  else:
  
    if details['state'] == "ON":
      _switch_on(appliance_code)
    elif details["state"] == "OFF":
      _switch_off(appliance_code)
    else:
      raise Exception("state not supported. Must be either \"ON\" or \"OFF\".")

def action_command(details):
  """Send an action command
  
  Sends the specified command to the homevision through netio interface.
  
  Args:
    details: {"command": string} 
  """
  if "command" not in details:
    raise Exception("Command not specified")

  if details["command"] not in actions.keys():
    raise Exception("Command not supported. Must be one of: " + ",".join(actions.keys()))

  actions[details["command"]]()
  

def _switch_on(code):
  _send_command(b"action flag set 56; flag clear 57; flag set 58; \
    macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100")
 
def _switch_off(code):
  _send_command(b"action flag clear 56; flag set 57; flag set 58; \
  macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100")
  
def _run_macro(code):
  _send_command(b'action macro run ' + bytes(str(code), encoding="ascii") + '; __wait 100')

 
def _send_command(command):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(("192.168.1.138", 11090))
  s.send(b"auth b2l0ZW46MnA4NzFrNGVxag\n")
  s.send(command)
  s.close()
  
if __name__ == "__main__":
  while True:
    command = raw_input("command:")
    print(command)
    if command == "on":
      on_off_command({"state": "ON", "appliance": "LANDING LIGHTS"})
    elif command == "off":
      on_off_command({"state": "OFF", "appliance": "LANDING LIGHTS"})
    else:
      print("not supported")
