__author__ = 'adewinter'
from django import forms
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import RadioSelect, HiddenInput


class BroadcastForm(forms.Form):
    sender_number = forms.CharField(max_length=15)
    contacts = forms.CharField(max_length=None) #list of contact ID's as selected by the Datatable present on the template page
    groups = forms.CharField(max_length=None) #list of group ID's as selected by the Datable present on the template page
    message_text = forms.CharField(widget=forms.Textarea, max_length=255)