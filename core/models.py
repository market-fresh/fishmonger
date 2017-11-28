from django.db import models

# Create your models here.
from django.utils import timezone
import uuid as uuidlib

class TimeStampedModelManager(models.Manager):

    def save(self, **kwargs):
        kwargs['updated_date'] = timezone.now()
        return super().save(**kwargs)

class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

#    slug = models.SlugField(unique=True)
    uuid = models.UUIDField(db_index=True, default=uuidlib.uuid4, editable=False)

    objects = TimeStampedModelManager()

    class Meta:
        abstract = True
