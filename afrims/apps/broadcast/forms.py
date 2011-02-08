__author__ = 'adewinter'
from django import forms
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import RadioSelect, HiddenInput



class ContactListField(forms.CharField):
     def to_python(self, value):
        "Normalize data to a list of strings."

        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(',')


class BroadcastForm(forms.Form):
    sender_number = forms.CharField(max_length=15, required=True)
    contacts = ContactListField(max_length=None, required=False, error_messages={'required': 'Please select one or more contacts to send the message to'}) #list of contact ID's as selected by the Datatable present on the template page
    groups = ContactListField(max_length=None, label='Groups List Selection', required=False, error_messages={'required': 'Please select a group/groups to send the message to'}) #list of group ID's as selected by the Datable present on the template page
    message_text = forms.CharField(widget=forms.Textarea, max_length=255)




    def clean(self):
        cleaned_data = self.cleaned_data
        contacts = cleaned_data.get("contacts")
        groups = cleaned_data.get("groups")

        if not contacts and not groups:
            print 'HURROO ERROR IN FORM %s %s' % (groups, contacts)
            raise forms.ValidationError("You must select some recipients (either Contacts, or Groups, or both)")

        # Always return the full collection of cleaned data.
        return cleaned_data

    def clean_contacts(self):
        c = self.cleaned_data['contacts']
        newc = []
        try:
            for item in c:
                newc.append(int(item))

        except ValueError:
            raise forms.ValidationError("Validation Error in Contacts FormField")

        return newc

    def clean_groups(self):
        g = self.cleaned_data['groups']
        newg = []
        try:
            for item in g:
                newg.append(int(item))

        except ValueError:
            raise forms.ValidationError("Validation Error in Groups FormField %s" % str(g))
        return newg
                


