
import socket

appliance_codes = {
  "DOWNSTAIRS BATHROOM MAIN LIGHTS"     : 8,
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
  "TOILET LIGHTS"                       : 87,
  "DOWNSTAIRS BATHROOM MIRROR LIGHTS"   : 145,
  
  "HEATING"                             : 0,
  "ALL LIGHTS"                          : 5,
  "FRONT LIGHTS"                        : 6,
  "BACK LIGHTS"                         : 7,
}

def on_off_command(details): 
  if "appliance" not in details:
    raise Exception("appliance not specified")
  elif "state" not in details:
    raise Exception("state not specified")

  if details["appliance"] not in appliance_codes.keys():
    raise Exception("appliance not supported. Must be one of: " + ",".join(appliance_codes.keys()))

  appliance_code = appliance_codes[details["appliance"]]
  
  if details["appliance"] in ["ALL LIGHTS", "FRONT LIGHTS", "BACK LIGHTS"]:
    run_macro(appliance_code)
  else:
  
    if details['state'] == "ON":
      switch_on(appliance_code)
    elif details["state"] == "OFF":
      switch_off(appliance_code)
    else:
      raise Exception("state not supported. Must be either \"ON\" or \"OFF\".")

def switch_on(code):
  send_command(b"action flag set 56; flag clear 57; flag set 58; \
    macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100")
 
def switch_off(code):
  send_command(b"action flag clear 56; flag set 57; flag set 58; \
  macro run " + bytes(str(code), encoding="ascii") + b"; __wait 100")
  
def run_macro(code):
  send_command(b'action macro run ' + bytes(str(code), encoding="ascii") + '; __wait 100')

def send_command(command):
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
      sendApplianceCommand({"state": "ON", "appliance": "LANDING LIGHTS"})
    elif command == "off":
      sendApplianceCommand({"state": "OFF", "appliance": "LANDING LIGHTS"})
    else:
      print("not supported")
