from django.db import models

from rapidsms.models import Contact

class CatchallMessage(models.Model):
    contact = models.ForeignKey(Contact)
    timestamp = models.DateTimeField(auto_now_add=True)
