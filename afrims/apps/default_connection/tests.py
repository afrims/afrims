from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict

from rapidsms.models import Contact, Backend, Connection

from afrims.tests.testcases import CreateDataTest

from afrims.apps.groups.models import Group


class DefaultConnectionTest(CreateDataTest):

    def test_backend_with_create(self):
        """ New contacts should be associated with a connection """
        backend = self.create_backend()
        contact = self.create_contact()
        connection = contact.get_or_create_connection()

#         form = group_forms.ContactForm(data)
#         self.assertTrue(form.is_valid())
#         contact = form.save()
#         self.assertEqual(contact.default_connection.backend.pk, backend.pk)
# 
#     def test_backend_with_existing_connection(self):
#         """ New contacts should auto associate with existing connections """
#         backend = self.create_backend()
#         connection = self.create_connection({'backend': backend})
#         data = self._data({'default_backend': backend.pk,
#                            'phone': connection.identity})
#         form = group_forms.ContactForm(data)
#         self.assertTrue(form.is_valid())
#         contact = form.save()
#         self.assertEqual(contact.default_connection.pk, connection.pk)
