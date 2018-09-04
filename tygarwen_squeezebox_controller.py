
from squeezebox_controller import SqueezeBoxController, UserException

class TygarwenSqueezeBoxController(SqueezeBoxController):
  
  def __init__(self, server_ip="192.168.1.126", server_port=9000, main_squeezebox=None):
    super().__init__(server_ip, server_port, lambda name: name.split("(", 1)[0][:-1])
    
    def radio4(helper, details):
      if "player" not in details:
        raise Exception("Player not specified")
      action_url = helper['base_url'] + "/plugins/Favorites/index.html?action=play&index=9&player="
      helper['requests'].get(action_url+helper['player_lookup'][details['player']])
      
    main_squeezebox_return_volume = None
    def quiet(helper):
      nonlocal main_squeezebox_return_volume
      if main_squeezebox != None and main_squeezebox_return_volume == None:
        player = helper['player_lookup'][main_squeezebox]
        info = helper['get_player_info'](player)
        main_squeezebox_return_volume = info['mixer volume']
        helper['make_request'](player, ["mixer","volume","20"])

    def return_volume(helper):
      nonlocal main_squeezebox_return_volume
      if main_squeezebox != None and main_squeezebox_return_volume != None:
        player = helper['player_lookup'][main_squeezebox]
        helper['make_request'](player, ["mixer","volume",str(main_squeezebox_return_volume)])
        main_squeezebox_return_volume = None

    self.add_custom_command("radio4", radio4)
    self.add_custom_command("quiet", quiet, False)
    self.add_custom_command("return_volume", return_volume, False)
  
  
  def play_radio4(self, details):
    """Plays BBC Radio 4
    
    Plays BBC radio 4 via the favourite

    Args:
      details: {"player": string}
    """
    self.custom_command("radio4", details)

  def quiet(self):
    """makes the main player nearly silent"""
    self.custom_command("quiet")

  def return_volume(self):
    """returns the main player volume to previous level"""
    self.custom_command("return_volume")
