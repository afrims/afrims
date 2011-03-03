from django import forms

from afrims.apps.groups.models import Group
from afrims.apps.groups.lookups import ContactLookup

from rapidsms.models import Contact

from selectable import forms as selectable


__all__ = ('GroupForm', 'ContactForm')


class GroupForm(forms.ModelForm):

    contacts = selectable.AutoCompleteSelectMultipleField(ContactLookup)

    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            pks = list(self.instance.contacts.values_list('pk', flat=True))
            self.initial['contacts'] = [[], pks]
        # help_text = 'Begin typing to search contact names'
        # self.fields['contacts'].help_text = help_text


class ContactForm(forms.ModelForm):
    """ Form for managing contacts """

    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.none())

    class Meta:
        model = Contact
        exclude = ('language',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.pk:
            kwargs['initial'] = {'groups': instance.groups.all()}
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget = forms.CheckboxSelectMultiple()
        self.fields['groups'].queryset = Group.objects.order_by('name')

    def save(self, commit=True):
        instance = super(ContactForm, self).save()
        instance.groups = self.cleaned_data['groups']
        return instance
