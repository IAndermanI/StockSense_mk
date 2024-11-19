from collections import defaultdict
from backend.items import get_items

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
        self.wants_to_sell = None
        self.deposited = 0
        self.items_to_buy = []
        self.lobby_code = None

    def set_default_settings(self):
        self.username = ""
        self.inventory = defaultdict(int)
        self.balance = 100
        self.wants_to_buy = None
        self.wants_to_sell = None
        self.deposited = 0
        self.items_to_buy = []
        self.lobby_code = None

    def buy_item(self, item_name, quantity):
        if quantity <= 0 or item_name not in self.items_to_buy:
            return False
        elif get_items(self.lobby_code).get_price(item_name) * quantity <= self.balance:
            self.inventory[item_name] += quantity
            self.balance -= get_items(self.lobby_code).get_price(item_name) * quantity
            return True
        return False

    def sell_item(self, item_name, quantity):
        if quantity < 0:
            return False
        elif item_name in self.inventory and quantity <= self.inventory[item_name]:
            self.inventory[item_name] -= quantity
            if self.inventory[item_name] == 0:
                self.inventory.pop(item_name)
            self.balance += get_items(self.lobby_code).get_price(item_name, False) * quantity
            return True
        return False

    def deposit(self, quantity):
        if quantity < 0:
            return False
        elif quantity <= self.balance:
            self.deposited += quantity
            self.balance -= quantity
            return True
        return False

    def check_inventory(self):
        message = f"Денег осталось: {self.balance:.2f}"
        for key in self.inventory.keys():
            message += f"\n{key}: {self.inventory[key]}"
        message += f"\nДенег на вкладе: {self.deposited}"
        message += f"\nИтого: {self.get_total_assets():.2f}"
        return message

    def get_total_assets(self) -> int:
        value = self.balance + self.deposited
        for item_name in self.inventory:
            value += get_items(self.lobby_code).get_price(item_name, False) * self.inventory[item_name]
        return value

get_player = PlayerFactory()
