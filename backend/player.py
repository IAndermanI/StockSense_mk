from collections import defaultdict
from backend.items import items

class PlayerFactory:
    _instances = {}

    def __call__(self, user_id, *args, **kwargs):
        if user_id not in self._instances:
            self._instances[user_id] = Player(user_id)
        return self._instances[user_id]

class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self.username = ""
        self.inventory = defaultdict(int)
        self.balance = 100
        self.wants_to_buy = None
        self.items_to_buy = []

    def buy_item(self, item_name, quantity):
        if quantity < 0 or item_name not in self.items_to_buy:
            return False
        elif items.get_price(item_name) * quantity <= self.balance:
            self.inventory[item_name] += quantity
            self.balance -= items.get_price(item_name) * quantity
            return True
        return False

    def sell_item(self, item_name, quantity):
        if quantity < 0:
            return False
        elif item_name in self.inventory and quantity <= self.inventory[item_name]:
            self.inventory[item_name] -= quantity
            self.balance += items.get_price(item_name) * quantity
            return True
        return False

    def check_inventory(self):
        message = f"Денег осталось: {self.balance}"
        for key in self.inventory.keys():
            message += f"\n{key}: {self.inventory[key]}"
        return message

    def get_total_assets(self) -> int:
        value = self.balance
        for item_name in self.inventory:
            value += items.get_price(item_name) * self.inventory[item_name]
        return value

get_player = PlayerFactory()
