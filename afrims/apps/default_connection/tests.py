from afrims.tests.testcases import CreateDataTest


class DefaultConnectionTest(CreateDataTest):

    def test_without_primary_backend(self):
        """ Random backend is chosen if contact's default is not set """
        backend = self.create_backend()
        contact = self.create_contact()
        connection = contact.get_or_create_connection()
        self.assertEqual(connection.backend_id, backend.pk)
        self.assertEqual(connection.identity, contact.phone)

    def test_with_primary_backend(self):
        """ New connection should have contact's default backend """
        backend1 = self.create_backend()
        backend2 = self.create_backend()
        contact = self.create_contact({'primary_backend': backend2})
        connection = contact.get_or_create_connection()
        self.assertEqual(connection.backend_id, backend2.pk)

    def test_conn(self):
        """ New connection should have contact's default backend """
        backend = self.create_backend()
        contact = self.create_contact({'primary_backend': backend})
        contact.set_primary_connection()
        contact.save()
        self.assertEqual(contact.primary_backend_id,
                         contact.primary_connection.backend_id)
