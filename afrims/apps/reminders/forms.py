from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory

from rapidsms.models import Contact

from afrims.apps.groups.models import Group
from afrims.apps.groups.validators import validate_phone
from afrims.apps.groups.utils import normalize_number
from afrims.apps.reminders import models as reminders


NotificationFormset = modelformset_factory(reminders.Notification,
                                           can_delete=True)

XML_DATE_FORMATS = ('%b  %d %Y ',)
XML_TIME_FORMATS = ('%H:%M', )

class PatientForm(forms.ModelForm):

    date_enrolled = forms.DateField(input_formats=XML_DATE_FORMATS)
    next_visit = forms.DateField(input_formats=XML_DATE_FORMATS,
                                 required=False)
    reminder_time = forms.TimeField(input_formats=XML_TIME_FORMATS,
                                    required=False)

    class Meta(object):
        model = reminders.Patient
        exclude = ('raw_data', 'contact')

    def clean_mobile_number(self):
        mobile_number = normalize_number(self.cleaned_data['mobile_number'])
        validate_phone(mobile_number)
        return mobile_number

    def save(self, payload):
        instance = super(PatientForm, self).save(commit=False)
        instance.raw_data = payload
        instance.raw_data.status = 'success'
        instance.raw_data.save()
        # get or create associated contact record
        if not instance.contact_id:
            subject_number = instance.subject_number
            contact, _ = Contact.objects.get_or_create(name=subject_number)
            instance.contact = contact
        instance.contact.phone = instance.mobile_number
        instance.contact.pin = instance.pin
        instance.contact.save()
        instance.save()
        # add to subject group
        group_name = settings.DEFAULT_SUBJECT_GROUP_NAME
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.contact.groups.add(group)
        return instance
