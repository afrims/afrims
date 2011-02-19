
from django import forms

from afrims.apps.groups.models import Group


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = _(u"Group code")
        self.fields['name'].label = _(u"Group name")
        contacts = Contact.objects.order_by('last_name', 'first_name')
        self.fields['recipients'].queryset = contacts
        self.fields['recipients'].label = _(u"Group recipients")

