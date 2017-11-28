from django.db import models

# Create your models here.
from core.models import TimeStampedModel
from fish.models import Fish

class Purchase_Order(TimeStampedModel):
    pass

class Purchase_Order_Item(TimeStampedModel):
  purchase_order = models.ForeignKey('Purchase_Order', on_delete=models.CASCADE)
  fish = models.ForeignKey('fish.Fish', on_delete=models.CASCADE)
  quantity = models.FloatField(default=0)
  weight = models.FloatField(default=0)
  buying_cost = models.FloatField(default=0)
  selling_cost = models.FloatField(default=0)
