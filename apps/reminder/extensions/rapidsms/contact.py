'''
Created on Jan 6, 2011

@author: adewinter
'''
from django.db import models
from apps.reminder.models import Group

class ContactType(models.Model):
    groups = models.ManyToManyField(Group, blank=True, null=True)
    
    class Meta:
        abstract = True
    