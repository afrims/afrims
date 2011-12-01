from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from rapidsms.models import Backend

from afrims.apps.groups.utils import format_number


class ContactExtra(models.Model):
    """ Abstract model to extend the RapidSMS Contact model """

    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=64, blank=True)

    def save(self, **kwargs):
        self.name = "%s %s" % (self.first_name, self.last_name)
        super(ContactExtra, self).save(**kwargs)

    class Meta:
        abstract = True

    @property
    def formatted_phone(self):
        return format_number(self.phone)

    def __unicode__(self):
        try:
            patient = self.patient_set.all()[0]
            if(patient.subject_number):
                return patient.subject_number
            else:
                return self.name
        except:
            return self.name

