from django.conf import settings

from afrims.tests.testcases import CreateDataTest


class DefaultConnectionTest(CreateDataTest):

    def test_defined_primary_backend(self):
        """ Random backend is chosen if contact's default is not set """
        backend = self.create_backend()
        contact = self.create_contact({'primary_backend': backend})
        connection = contact.get_primary_connection()
        self.assertEqual(connection.backend_id, backend.pk)
        self.assertEqual(connection.contact_id, contact.pk)

    def test_random_primary_backend(self):
        """ Random backend is fallback """
        backend = self.create_backend()
        contact = self.create_contact()
        if hasattr(settings, 'PRIMARY_BACKEND'):
            backend.name = settings.PRIMARY_BACKEND
            backend.save()
        connection = contact.get_primary_connection()
        self.assertEqual(connection.backend_id, backend.pk)
        self.assertEqual(connection.contact_id, contact.pk)

    def test_backend_setting(self):
        """ Test specified backend """
        self.create_backend()
        backend = self.create_backend()
        contact = self.create_contact()
        connection = contact.get_primary_connection(backend_name=backend.name)
        self.assertEqual(connection.backend_id, backend.pk)
        self.assertEqual(connection.contact_id, contact.pk)
