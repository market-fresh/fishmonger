from django.db import models
from django.conf import settings

# Create your models here.
from core.models import TimeStampedModel

class Stall(TimeStampedModel):
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=50, blank=True, default='')
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, default='Singapore')
    city  = models.CharField(max_length=50, default='Singapore')
    unit_no = models.CharField(max_length=10, blank=True)
    postal_code = models.CharField(max_length=6)
    contact_no = models.CharField(max_length=15, blank=True)
