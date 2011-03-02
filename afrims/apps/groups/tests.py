from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from afrims.tests.testcases import CreateDataTest

from afrims.apps.groups.models import Group
from afrims.apps.groups import forms as group_forms


class GroupFormTest(CreateDataTest):
    def test_create_contact(self):
        """ Test contact creation functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        name = self.random_string(16)
        data =  {
            'name': name,
            'groups': [group1.pk],
        }
        form = group_forms.ContactForm(data)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.name, name)
        self.assertEqual(contact.groups.count(), 1)
        self.assertTrue(contact.groups.filter(pk=group1.pk).exists())
        self.assertFalse(contact.groups.filter(pk=group2.pk).exists())

    def test_edit_contact(self):
        """ Test contact creation functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        contact = self.create_contact()
        contact.groups.add(group1)
        data =  {
            'name': contact.name,
            'groups': [group2.pk],
        }
        form = group_forms.ContactForm(data, instance=contact)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.groups.count(), 1)
        self.assertFalse(contact.groups.filter(pk=group1.pk).exists())
        self.assertTrue(contact.groups.filter(pk=group2.pk).exists())
