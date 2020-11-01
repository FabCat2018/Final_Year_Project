from django.db import models
from json import JSONEncoder


class Item(models.Model):
    item_id = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title


class Game:
    def __init__(self, seller, price):
        self.seller = seller
        self.price = price

    def __str__(self):
        return dict(self.seller, self.price)


class GameEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
