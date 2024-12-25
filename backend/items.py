from backend.sceneries.teenagers import teenagers_scenery
from backend.sceneries.test import test_scenery
from backend.sceneries.conferention import conferention_scenery
from backend.sceneries.seven_eight_grade import seven_eight_grade_scenery

sceneries = ['teenagers', 'test', 'conferention', '7-8 класс']

class ItemsFactory:
    _instances = {}

    def __call__(self, lobby_code, *args, **kwargs):
        if lobby_code not in self._instances:
            self._instances[lobby_code] = Items(lobby_code)
        return self._instances[lobby_code]
    
class Items:
    def __init__(self, lobby_code, round_number=1):
        self.items = teenagers_scenery
        self.round_number = round_number
        self.max_rounds = len(teenagers_scenery)
        self.lobby_code = lobby_code
    
    def set_scenery(self, scenery_name):
        if scenery_name == 'teenagers':
            self.items = teenagers_scenery
        elif scenery_name == 'test':
            self.items = test_scenery
        elif scenery_name == 'conferention':
            self.items = conferention_scenery
        elif scenery_name == '7-8 класс':
            self.items = seven_eight_grade_scenery
        else: # default
            self.items = teenagers_scenery

        self.max_rounds = len(self.items)

    def get_items_list(self):
        return list(self.items[self.round_number - 1].keys())

    def get_price(self, item_name, is_buy=True):
        is_buying = 0 if is_buy else 1
        return self.items[self.round_number - 1][item_name][is_buying]
    
get_items = ItemsFactory()
