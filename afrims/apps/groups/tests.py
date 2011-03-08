from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict

from rapidsms.models import Contact, Backend, Connection

from afrims.tests.testcases import CreateDataTest

from afrims.apps.groups.models import Group
from afrims.apps.groups import forms as group_forms


class GroupFormTest(CreateDataTest):

    def create_contact(self, data={}):
        """ Override super's create_contact to include extension fields """
        defaults = self._data()
        defaults.update(data)
        return Contact.objects.create(**defaults)

    def _data(self, initial_data={}, instance=None):
        """ Helper function to generate form-like POST data """
        if instance:
            data = model_to_dict(instance)
        else:
            data = {
                'first_name': self.random_string(8),
                'last_name': self.random_string(8),
                'email': 'test@abc.com',
                'phone': '1112223333',
            }
        data.update(initial_data)
        return data

    def test_create_contact(self):
        """ Test contact creation functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        data = self._data({'groups': [group1.pk]})
        form = group_forms.ContactForm(data)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.first_name, data['first_name'])
        self.assertEqual(contact.groups.count(), 1)
        self.assertTrue(contact.groups.filter(pk=group1.pk).exists())
        self.assertFalse(contact.groups.filter(pk=group2.pk).exists())

    def test_edit_contact(self):
        """ Test contact edit functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        contact = self.create_contact()
        contact.groups.add(group1)
        data = self._data({'groups': [group2.pk]}, instance=contact)
        form = group_forms.ContactForm(data, instance=contact)
        self.assertTrue(form.is_valid(), dict(form.errors))
        contact = form.save()
        self.assertEqual(contact.groups.count(), 1)
        self.assertFalse(contact.groups.filter(pk=group1.pk).exists())
        self.assertTrue(contact.groups.filter(pk=group2.pk).exists())

    def test_backend_with_create(self):
        """ New contacts should be associated with a connection """
        backend = self.create_backend()
        data = self._data({'default_backend': backend.pk})
        form = group_forms.ContactForm(data)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.default_connection.backend.pk, backend.pk)

    def test_backend_with_existing_connection(self):
        """ New contacts should auto associate with existing connections """
        backend = self.create_backend()
        connection = self.create_connection({'backend': backend})
        data = self._data({'default_backend': backend.pk,
                           'phone': connection.identity})
        form = group_forms.ContactForm(data)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.default_connection.pk, connection.pk)
