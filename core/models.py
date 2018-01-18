from django.db import models

# Create your models here.
from django.utils import timezone
import uuid as uuidlib

class TimeStampedModelManager(models.Manager):
    """
    Model manager class definition to handle updated_date during the save method call
    """

    def save(self, **kwargs):
        kwargs['updated_date'] = timezone.now()
        return super().save(**kwargs)

class TimeStampedModel(models.Model):
    """
    Model class definition for all models to implement the created_date and updated_date fields into the all models
    """
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(db_index=True, default=uuidlib.uuid4, editable=False)

    objects = TimeStampedModelManager()

    class Meta:
        abstract = True
