
import socket
from homevision_netio_controller import UserException, HomeVisionController, Macro, Command, user_exception

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
  "HEATING HOUR"                        : Macro(0),
  "HEATING OFF"                         : Macro(1),
  "HEATING MAN ADVANCE"                 : Command(b'action flag set 76; __wait 500; action pe run 10; __wait 200'),
  "HOT WATER TOPUP"                     : Macro(2),
  "HOT WATER OFF"                       : Macro(4),
  "ALL LIGHTS OFF"                      : Macro(5),
  "FRONT LIGHTS TRIGGER"                : Macro(6),
  "BACK LIGHTS TRIGGER"                 : Macro(7),
  "DOWNSTAIRS BATHROOM LEFT RADIATOR"   : Macro(16),
  "DOWNSTAIRS BATHROOM RIGHT RADIATOR"  : Macro(20),
  "DOWNSTAIRS BATHROOM RADIATORS"       : (Macro(16), Macro(20)),
  "UPSTAIRS BATHROOM LEFT RADIATOR"     : Macro(65),
  "UPSTAIRS BATHROOM RIGHT RADIATOR"    : Macro(69),
  "UPSTAIRS BATHROOM RADIATORS"         : (Macro(65), Macro(69)),
  "DOOR BELL"                           : Macro(117)
}

process_actions = {
  "VEG WATERING": {"START": Macro(110), "STOP": Macro(108)},
  "FRUIT WATERING": {"START": Macro(116), "STOP": Macro(114)},
  "PATIO WATERING": {"START": Macro(113), "STOP": Macro(11)},
  "POND TOPUP": {"START": Macro(118), "STOP": Macro(111)},
  "ALL WATERING": {
    "START": Command(b'action flag set 70 ; macro run 119 ; __wait 200'),
    "STOP": UserException("Cannot stop this process") }
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

flag_return_values = {
  False: ["Off", "No", "Vacant", "Clear"],
  True: ["On", "Yes", "Occupied", "Set", "Pumping", "Watering", "Heating", "Running"]
}

on_off_commands = {
  "ON": lambda code: b"action flag set 56; flag clear 57; flag set 58; \
    macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100",
  "OFF": lambda code: b"action flag clear 56; flag set 57; flag set 58; \
    macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100"
}

class TygarwenHomeVisionController(HomeVisionController):
  def __init__(self, ip_address, port, auth):
    super().__init__(ip_address, port, auth, on_off_appliance_codes, actions,
      process_actions, var_queries, flag_queries, flag_return_values, on_off_commands)

  def var_query(self, details):
    __doc__ = super().__doc__
    
    val = super().var_query(details)
    
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
