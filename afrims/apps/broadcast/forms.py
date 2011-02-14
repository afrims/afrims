import datetime

from django import forms
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import RadioSelect, HiddenInput
from django.utils.encoding import smart_unicode

from afrims.apps.broadcast.models import Broadcast


class BroadcastForm(forms.ModelForm):
    """ Form to send a broadcast message """

    SEND_CHOICES = (
        ('now', 'Now'),
        ('later', 'Later'),
    )
    when = forms.ChoiceField(label='Send', choices=SEND_CHOICES)

    class Meta(object):
        model = Broadcast
        exclude = ('date_created', 'date_last_notified', 'date_next_notified')

    def __init__(self, *args, **kwargs):
        super(BroadcastForm, self).__init__(*args, **kwargs)
        picker_class = 'datetimepicker'
        self.fields['date'].label = 'Start date'
        self.fields['date'].required = False
        self.fields['date'].widget.attrs['class'] = picker_class
        self.fields['schedule_end_date'].widget.attrs['class'] = picker_class
        widget_class = 'multiselect'
        self.fields['weekdays'].help_text = ''
        self.fields['weekdays'].widget.attrs['class'] = widget_class
        self.fields['months'].help_text = ''
        self.fields['months'].widget.attrs['class'] = widget_class
        self.fields['groups'].help_text = ''
        self.fields['groups'].widget.attrs['class'] = widget_class
        # hide disabled frequency in form
        choices = list(Broadcast.REPEAT_CHOICES)
        choices.pop(0)
        self.fields['schedule_frequency'].choices = choices
        self.fields.keyOrder = ('when', 'date', 'schedule_frequency', 
                                'schedule_end_date','weekdays', 'months',
                                'body', 'groups')

    def clean(self):
        when = self.cleaned_data['when']
        date = self.cleaned_data['date']
        if when == 'later' and not date:
            raise forms.ValidationError('Start date is required for future broadcasts')
        return self.cleaned_data

    def save(self, commit=True):
        broadcast = super(BroadcastForm, self).save(commit=False)
        if self.cleaned_data['when'] == 'now':
            broadcast.date = datetime.datetime.now()
        if commit:
            broadcast.save()
            self.save_m2m()
        return broadcast

