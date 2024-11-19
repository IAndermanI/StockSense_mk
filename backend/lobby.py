from backend.round import Round
from random import randint
from backend.items import *
from backend.player import get_player

class LobbyFactory:
    _instances = {}

    def __call__(self, lobby_code=None, *args, **kwargs):
        if lobby_code is None:
            lobby_code = self.create_valid_lobby_code()
        if lobby_code not in self._instances:
            self._instances[lobby_code] = Lobby(lobby_code)
        return self._instances[lobby_code]

    def create_valid_lobby_code(self):
        lobby_code = randint(100000, 999999)
        while lobby_code in self.get_all_lobbies():
            lobby_code = randint(100000, 999999)
        return lobby_code

    def get_all_lobbies(self):
        return self._instances.keys()

class Lobby:
    def __init__(self, lobby_code):
        self.lobby_code = lobby_code
        self.is_over = False
        self.player_ids = []
        self.round = Round(lobby_code)
        get_items(lobby_code)

    def is_player_in_lobby(self, player_id):
        return player_id in self.player_ids

    def add_player(self, player_id):
        self.player_ids.append(player_id)
        get_player(player_id).set_default_settings()
        get_player(player_id).lobby_code = self.lobby_code

    def start_game(self):
        self.round = Round(self.lobby_code, player_ids=self.player_ids)

get_lobby = LobbyFactory()
