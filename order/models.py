from django.db import models

# Create your models here.
from core.models import TimeStampedModel
from fish.models import Fish
from purchase_order.models import Purchase_Order
from stall.models import Stall

class Order(TimeStampedModel):
    stall = models.ForeignKey('stall.Stall', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='')
    purchase_order = models.ForeignKey('purchase_order.Purchase_Order', null=True, on_delete=models.CASCADE)

class Order_Item(TimeStampedModel):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    fish = models.ForeignKey('fish.Fish', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='')
    quantity = models.FloatField(default=0)
    weight = models.FloatField(default=0)
    cost = models.FloatField(default=0)
