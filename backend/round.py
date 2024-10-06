from random import sample
from backend.player import get_player
from backend.items import items

class Round:
    def __init__(self, round_number=1, player_ids=[]):
        self.round_number = round_number
        self.player_ids = player_ids
        self.items_to_pick = {}

    def start_new_round(self):
        self.round_number += 1
        items.round_number += 1
        for player_id in self.player_ids:
            if self.round_number <= 10:
                get_player(player_id).balance += 50
            get_player(player_id).balance += 1.2 * get_player(player_id).deposited
            get_player(player_id).deposited = 0


    def get_items_to_pick(self, number_of_items=3):
        items_by_players = {}
        items_list = items.get_items_list()
        items_to_pick = []
        for item in items_list:
            if items.get_price(item) > 0:
                items_to_pick.append(item)

        for player_id in self.player_ids:
            items_by_players[player_id] = sample(items_to_pick, number_of_items)
            get_player(player_id).items_to_buy = items_by_players[player_id]
        return items_by_players

    def get_top_players(self):
        players_and_assets = {}
        for player_id in self.player_ids:
            players_and_assets[get_player(player_id).username] = get_player(player_id).get_total_assets()
        top_players = sorted(players_and_assets, key=lambda username: -players_and_assets[username])
        return top_players

