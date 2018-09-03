
from squeezebox_controller import SqueezeBoxController, UserException

class TygarwenSqueezeBoxController(SqueezeBoxController):
  
  def __init__(self, server_ip="192.168.1.126", server_port=9000):
    super().__init__(server_ip, server_port, lambda name: name.split("(", 1)[0][:-1])
    
    def radio4(helper, details):
      if "player" not in details:
        raise Exception("Player not specified")
      action_url = helper['base_url'] + "/plugins/Favorites/index.html?action=play&index=9&player="
      helper['requests'].get(action_url+helper['player_lookup'][details['player']])
      
    self.add_custom_command("radio4", radio4)
  
  
  def play_radio4(self, details):
    """Plays BBC Radio 4
    
    Plays BBC radio 4 via the favourite

    Args:
      details: {"player": string}
    """
    self.custom_command("radio4", details)

