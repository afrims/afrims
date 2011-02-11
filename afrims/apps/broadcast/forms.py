from django import forms
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import RadioSelect, HiddenInput
from django.utils.encoding import smart_unicode

from afrims.apps.broadcast.models import Broadcast


class BroadcastForm(forms.ModelForm):
    """ Form to send a send a broadcast message """

    class Meta(object):
        model = Broadcast
        exclude = ('date_created', 'date_last_notified', 'date_next_notified')

    def __init__(self, *args, **kwargs):
        super(BroadcastForm, self).__init__(*args, **kwargs)
        picker_class = 'datetimepicker'
        self.fields['schedule_start_date'].widget.attrs['class'] = picker_class
        self.fields['schedule_end_date'].widget.attrs['class'] = picker_class
        widget_class = 'multiselect'
        self.fields['weekdays'].help_text = ''
        self.fields['weekdays'].widget.attrs['class'] = widget_class
        self.fields['months'].help_text = ''
        self.fields['months'].widget.attrs['class'] = widget_class
        self.fields['groups'].help_text = ''
        self.fields['groups'].widget.attrs['class'] = widget_class
        self.fields.keyOrder = ('schedule_start_date', 'schedule_end_date',
                                'schedule_frequency', 'weekdays', 'months',
                                'body', 'groups')

    def save(self, commit=True):
        broadcast = super(BroadcastForm, self).save(commit=False)
        broadcast.set_next_date()
        if commit:
            broadcast.save()
        return broadcast

