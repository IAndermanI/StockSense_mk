items_1 = {
    "Хомяк": 1,
    "Найки про": 50,
    "Акции Газпрома": 10,
    "Робакс": 2
}

items_2 = {
    "Хомяк": 2,
    "Найки про": 50,
    "Акции Газпрома": 15,
    "Робакс": 2
}

items_3 = {
    "Хомяк": 0,
    "Найки про": 40,
    "Акции Газпрома": 20,
    "Робакс": 1
}

class Items:
    def __init__(self, round_number=1):
        self.items = [items_1, items_2, items_3]
        self.round_number = round_number

    def get_items_list(self):
        return list(self.items[self.round_number - 1].keys())

    def get_price(self, item_name):
        return self.items[self.round_number - 1][item_name]

items = Items(1)
