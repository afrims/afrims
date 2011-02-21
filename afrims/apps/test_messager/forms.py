from django import forms

from rapidsms.models import Backend, Connection

from rapidsms.contrib.messaging.utils import send_message


class MessageForm(forms.Form):
    backend = forms.ModelChoiceField(queryset=Backend.objects.all())
    number = forms.CharField()
    message = forms.CharField(widget=forms.HiddenInput())

    def save(self):
        number = self.cleaned_data['number']
        backend = self.cleaned_data['backend']
        connection, _ = Connection.objects.get_or_create(backend=backend,
                                                         identity=number)
        return send_message(connection, self.cleaned_data['message'])

