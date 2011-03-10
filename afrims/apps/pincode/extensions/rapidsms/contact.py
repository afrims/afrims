from django.db import models


class ContactPin(models.Model):
    pin = models.CharField(max_length=20, blank=True, help_text='A PIN code '
                           'for SMS authentication workflows.')
    
    class Meta:
        abstract = True
