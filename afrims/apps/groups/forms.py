import logging

from django import forms

from afrims.apps.groups.models import Group

from rapidsms.models import Contact, Backend


__all__ = ('GroupForm', 'ContactForm')


logger = logging.getLogger('afrims.apps.groups.forms')


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['contacts'].help_text = ''
        qs = Contact.objects.filter(patient__isnull=True).order_by('name')
        self.fields['contacts'].queryset = qs
        self.fields['contacts'].widget.attrs['class'] = 'horitzonal-multiselect'


class ContactForm(forms.ModelForm):
    """ Form for managing contacts """

    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.none())

    class Meta:
        model = Contact
        exclude = ('language', 'name')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.pk:
            pks = instance.groups.values_list('pk', flat=True)
            kwargs['initial'] = {'groups': list(pks)}
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget = forms.CheckboxSelectMultiple()
        self.fields['groups'].queryset = Group.objects.order_by('name')
        self.fields['groups'].required = False
        for name in ('first_name', 'last_name', 'email', 'phone'):
            self.fields[name].required = True

    def _get_connection(self, instance):
        """ Look for a connection related to specified phone and backend """
        from rapidsms.models import Connection
        if Backend.objects.count() > 0:
            if not instance.default_backend:
                # TODO: possibly make this a setting
                instance.default_backend = Backend.objects.all()[0]
            data = {'backend': instance.default_backend,
                    'identity': instance.phone}
            connection, _ = Connection.objects.get_or_create(**data)
            return connection

    def save(self, commit=True):
        instance = super(ContactForm, self).save()
        instance.groups = self.cleaned_data['groups']
        # if we find a connection, associate it with this contact
        connection = self._get_connection(instance)
        if connection:
            connection.contact = instance
            connection.save()
        return instance
