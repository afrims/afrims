from django.forms.models import modelformset_factory

from afrims.apps.reminders import models as reminders


NotificationFormset = modelformset_factory(reminders.Notification,
                                           can_delete=True)
