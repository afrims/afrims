from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return self.name

class ScheduledTaskUI(models.Model):
    repeat_frequencies = (('hourly','hourly'),
                            ('daily','daily'),
                            ('weekly','weekly'),
                            ('monthly','monthly'),
                            ('yearly','yearly'))
    description = models.CharField(max_length=255)
    repeat_frequency = models.CharField(max_length=12,choices=repeat_frequencies)
    
    