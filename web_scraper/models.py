from django.db import models


class Item(models.Model):
    item_id = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title
