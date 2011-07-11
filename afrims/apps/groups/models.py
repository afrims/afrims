from django.db import models

from rapidsms.models import Contact


class Group(models.Model):
    """ Organize RapidSMS contacts into groups """

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    is_editable = models.BooleanField(default=True)

    contacts = models.ManyToManyField(Contact, related_name='groups',
                                      blank=True)

    class Meta:
        permissions = (
            ("can_use_dashboard_tab", "Can use Dashboard tab"),
            ("can_use_send_a_message_tab", "Can use Send a Message tab"),
            ("can_use_appointment_reminders_tab", "Can use Appointment Reminders tab"),
            ("can_use_forwarding_tab", "Can use Forwarding tab"),
            ("can_use_groups_tab", "Can use Groups tab"),
            ("can_use_people_tab", "Can use People tab"),
            ("can_use_settings_tab", "Can use Settings tab"), # not implemented
        )

    def __unicode__(self):
        return self.name
