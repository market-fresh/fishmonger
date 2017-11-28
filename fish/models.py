from django.db import models

# Create your models here.
from core.models import TimeStampedModel

class Fish(TimeStampedModel):
      name = models.CharField(max_length=25)
      chinese_name = models.CharField(max_length=50, blank=True, default='')
      sequence = models.IntegerField(unique=True)
      #photo = models.ImageField(upload_to='fish/images/', blank=True)
