from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return self.name