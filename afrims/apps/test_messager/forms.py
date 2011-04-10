from django import forms
from django.conf import settings

from rapidsms.models import Backend, Connection
from rapidsms.messages import OutgoingMessage

from threadless_router.router import Router


class MessageForm(forms.Form):
    backend = forms.ModelChoiceField(queryset=Backend.objects.all())
    number = forms.CharField()
    message = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        if hasattr(settings, 'TEST_MESSAGER_BACKEND'):
            backend_name = settings.TEST_MESSAGER_BACKEND
            try:
                backend = Backend.objects.get(name=backend_name)
            except Backend.DoesNotExist:
                backend = None
            if backend:
                self.initial['backend'] = backend
                self.fields['backend'].widget = forms.HiddenInput()

    def save(self):
        number = self.cleaned_data['number']
        backend = self.cleaned_data['backend']
        connection, _ = Connection.objects.get_or_create(backend=backend,
                                                         identity=number)
        msg = OutgoingMessage(connection, self.cleaned_data['message'])
        router = Router()
        return router.backends[backend.name].send(msg)
