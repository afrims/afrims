import logging
import re

from django import forms
from rapidsms.conf import settings

from afrims.apps.groups.models import Group
from afrims.apps.groups.utils import format_number, normalize_number
from afrims.apps.groups.validators import validate_phone


from rapidsms.models import Contact, Backend


__all__ = ('GroupForm', 'ContactForm', 'ForwardingRuleFormset',)


logger = logging.getLogger('afrims.apps.groups.forms')


class FancyPhoneInput(forms.TextInput):

    def render(self, name, value, attrs=None):
        if value:
            value = format_number(value)
        return super(FancyPhoneInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        value = super(FancyPhoneInput, self).value_from_datadict(data, files, name)
        if value:
            value = normalize_number(value)
        return value


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        exclude = ('is_editable',)

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['contacts'].help_text = ''
#        qs = Contact.objects.filter(patient__isnull=True).order_by('name')
        qs = Contact.objects.all().order_by('patient__subject_number')
        self.fields['contacts'].queryset = qs
        self.fields['contacts'].widget.attrs['class'] = 'horitzonal-multiselect'


class ContactForm(forms.ModelForm):
    """ Form for managing contacts """

    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.none())
    phone = forms.CharField(validators=[validate_phone], required=True, widget=FancyPhoneInput)

    class Meta:
        model = Contact
        exclude = ('language', 'name', 'primary_backend', 'pin')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.pk:
            pks = instance.groups.values_list('pk', flat=True)
            kwargs['initial'] = {'groups': list(pks)}
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget = forms.CheckboxSelectMultiple()
        self.fields['groups'].queryset = Group.objects.exclude(name=settings.DEFAULT_SUBJECT_GROUP_NAME).order_by('name')
        self.fields['groups'].required = False
        for name in ('first_name', 'last_name', 'phone'):
            self.fields[name].required = True

    def save(self, commit=True):
        instance = super(ContactForm, self).save()
        instance.groups = self.cleaned_data['groups']
        return instance
