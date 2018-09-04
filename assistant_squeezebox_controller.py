
from squeezebox_controller import SqueezeBoxController, UserException

class AssistantSqueezeBoxController(SqueezeBoxController):
  
  def __init__(self, server_ip="192.168.0.100", server_port=9000, main_squeezebox=None):
    super().__init__(server_ip, server_port)
      
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

    self.add_custom_command("quiet", quiet, False)
    self.add_custom_command("return_volume", return_volume, False)
  
  def quiet(self):
    """makes the main player nearly silent"""
    self.custom_command("quiet")

  def return_volume(self):
    """returns the main player volume to previous level"""
    self.custom_command("return_volume")
