'''
Created on Jan 6, 2011

@author: adewinter
'''
from django.db import models
from apps.reminder.models import Group

class ContactType(models.Model):
    groups = models.ManyToManyField(Group)
    
    class Meta:
        abstract = True
    