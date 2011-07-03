from django.db import models

from rapidsms.models import Contact

class CatchallMessage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    identity = models.CharField(max_length=100)
