
from django import forms

from afrims.apps.groups.models import Group

from rapidsms.models import Contact


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        contacts = Contact.objects.order_by('name')
        self.fields['contacts'].queryset = contacts

