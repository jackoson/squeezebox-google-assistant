
import socket
from feedback import UserException

on_off_appliance_codes = {
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
  "DOWNSTAIRS BATHROOM MIRROR LIGHTS"   : 145
}

actions = {
  "HEATING HOUR"                        : lambda: _run_macro(0),
  "HEATING OFF"                         : lambda: _run_macro(1),
  "HEATING MAN ADVANCE"                 : lambda: _send_command(b'action flag set 76; __wait 500; action pe run 10; __wait 200'),
  "HOT WATER TOPUP"                     : lambda: _run_macro(2),
  "HOT WATER OFF"                       : lambda: _run_macro(4),
  "ALL LIGHTS OFF"                      : lambda: _run_macro(5),
  "FRONT LIGHTS TRIGGER"                : lambda: _run_macro(6),
  "BACK LIGHTS TRIGGER"                 : lambda: _run_macro(7),
  "DOWNSTAIRS BATHROOM LEFT RADIATOR"   : lambda: _run_macro(16),
  "DOWNSTAIRS BATHROOM RIGHT RADIATOR"  : lambda: _run_macro(20),
  "DOWNSTAIRS BATHROOM RADIATORS"       : lambda: (_run_macro(16), _run_macro(20)),
  "UPSTAIRS BATHROOM LEFT RADIATOR"     : lambda: _run_macro(65),
  "UPSTAIRS BATHROOM RIGHT RADIATOR"    : lambda: _run_macro(69),
  "UPSTAIRS BATHROOM RADIATORS"         : lambda: (_run_macro(65), _run_macro(69)),
  "DOOR BELL"                           : lambda: _run_macro(117)
}

def user_exception(s): raise UserException(s)

process_actions = {
  "VEG WATERING": {"START": lambda: _run_macro(110), "STOP": lambda: _run_macro(108)},
  "FRUIT WATERING": {"START": lambda: _run_macro(116), "STOP": lambda: _run_macro(114)},
  "PATIO WATERING": {"START": lambda: _run_macro(113), "STOP": lambda: _run_macro(11)},
  "POND TOPUP": {"START": lambda: _run_macro(118), "STOP": lambda: _run_macro(111)},
  "ALL WATERING": {
    "START": lambda: _send_command(b'action flag set 70 ; macro run 119 ; __wait 200'),
    "STOP": lambda: user_exception("Cannot stop this process") }
}

var_queries = {
  "HALL TEMP": 6,
  "OUTSIDE TEMP": 7,
  "LIGHT LEVEL": 8,
  "TANK TEMP": 81,
  "BATH COUNT": 82,
  "HEATING STATE": 93,
  "RAIN TODAY": (95, 96),
  "RAIN YESTERDAY": 97
}

flag_queries = {
  "SOLAR PUMP": 1,
  "HEATING": 3,
  "HOT WATER": 4,
  "HOUSE SECURE": 5,
  "RAINING": 79
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

  if details["appliance"] not in on_off_appliance_codes.keys():
    raise Exception("appliance not supported. Must be one of: " + ",".join(on_off_appliance_codes.keys()))

  appliance_code = on_off_appliance_codes[details["appliance"]]
  
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
  
def start_stop_command(details):
  """Starts or stops a process
  
  Sends the specified command to the homevision through netio interface to control the specified process.
  
  Args:
    details: {"action": string, "process": string} 
  """
  if "action" not in details:
    raise Exception("action not specified")
  elif "process" not in details:
    raise Exception("process not specified")

  if details["process"] not in process_actions.keys():
    raise Exception("process not supported. Must be one of: " + ",".join(process_actions.keys()))
  
  if details['action'] == "START":
    process_actions[details["process"]]["START"]()
  elif details["action"] == "STOP":
    process_actions[details["process"]]["STOP"]()
  else:
    raise Exception("action not supported. Must be either \"START\" or \"STOP\".")

def var_query(details):
  """Returns the answer to a query on variable
  
  Returns the answer to a query on the specified variable using netio
  
  Args:
    details: {"query": string} 
  """
  if "query" not in details:
    raise Exception("query not specified")
  
  if details["query"] not in var_queries.keys():
    raise Exception("query not supported. Must be one of: " + ",".join(var_queries.keys()))
  
  code = var_queries[details["query"]]
  if type(code) == int:
    val = _get_var(code)
  elif type(code) == tuple:
    val = [_get_var(c) for c in code]
  else:
    raise Exception("Internal Exception: code is not valid")
  
  if details["query"] in ["TANK TEMP", "HALL TEMP", "OUTSIDE TEMP"]:
    return "It is %d degrees"%(val)
  if details["query"] == "RAIN TODAY":
    return "There was %d point %d millimeters"%(val[0], val[1])
  if details["query"] == "RAIN YESTERDAY":
    return "There was %d millimeters"%(val)
  if details["query"] == "BATH COUNT":
    return "There are %d"%(val)
  else:
    return "It is %d"%(val)

def flag_query(details):
  """Returns the answer to a query on flag
  
  Returns the answer to a query on the specified variable using netio
  
  Args:
    details: {"query": string} 
  """
  if "query" not in details:
    raise Exception("query not specified")
  
  if details["query"] not in flag_queries.keys():
    raise Exception("query not supported. Must be one of: " + ",".join(flag_queries.keys()))
  
  val = _get_flag(flag_queries[details["query"]])
  
  return "yes" if val else "no"
  
 
def _switch_on(code):
  _send_command(b"action flag set 56; flag clear 57; flag set 58; \
    macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100")
 
def _switch_off(code):
  _send_command(b"action flag clear 56; flag set 57; flag set 58; \
  macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100")
  
def _run_macro(code):
  _send_command(b'action macro run ' + bytes(str(code), encoding="ascii") + b'; __wait 100')

 
def _send_command(command):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(("192.168.1.138", 11090))
  s.send(b"auth b2l0ZW46MnA4NzFrNGVxag\n")
  s.send(command)
  s.close()

def _get_var(id):
  return int(_run_read_command(b"get var state " + bytes(str(id), encoding="ascii")))

def _get_flag(id):
  ret = _run_read_command(b"get flag state " + bytes(str(id), encoding="ascii"))
  if ret in ["Off", "No", "Vacant", "Clear"]:
    return False
  elif ret in ["On", "Yes", "Occupied", "Set", "Pumping", "Watering", "Heating", "Running"]:
    return True
  else:
    raise Exception("Flag value not supported: " + ret)

def _run_read_command(command):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(("192.168.1.138", 11090))
  s.send(b"auth b2l0ZW46MnA4NzFrNGVxag\n")
  s.recv(10)
  s.send(command)
  s.send(b'\n')
  response = s.recv(10).decode(encoding="ascii").rstrip()
  s.close()
  return response
  
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
