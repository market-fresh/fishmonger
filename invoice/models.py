from django.db import models

# Create your models here.
from core.models import TimeStampedModel
from fish.models import Fish
from order.models import Order
from stall.models import Stall

class Invoice(TimeStampedModel):
  stall = models.ForeignKey('stall.Stall', on_delete=models.CASCADE)
  ice = models.FloatField(null=True)
  cash_float = models.FloatField(null=True)
  total_cost = models.FloatField()
  sales = models.FloatField(null=True)
  order = models.ForeignKey('order.Order', null=True, on_delete=models.CASCADE)

class Invoice_Item(TimeStampedModel):
  invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
  fish = models.ForeignKey('fish.Fish', on_delete=models.CASCADE)
  weight = models.FloatField(default=0)
  cost = models.FloatField(default=0)
  total = models.FloatField(null=True)
