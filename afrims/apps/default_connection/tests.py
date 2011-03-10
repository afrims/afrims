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

    def test_set_primary_connection(self):
        """ Primary connection should be updated based on primary backend """
        backend = self.create_backend()
        contact = self.create_contact({'primary_backend': backend})
        contact.set_primary_connection()
        contact.save()
        self.assertEqual(contact.primary_backend_id,
                         contact.primary_connection.backend_id)

    def test_update_primary_connection(self):
        """ Make sure connection changes if backend changes """
        connection1 = self.create_connection({'identity': '1112223333'})
        backend1 = connection1.backend
        contact = self.create_contact({'primary_backend': backend1,
                                       'primary_connection': connection1})
        backend2 = self.create_backend()
        contact.primary_backend = backend2
        contact.set_primary_connection()
        contact.save()
        self.assertNotEqual(contact.primary_connection_id, connection1.pk)

    def test_reuse_connection(self):
        """ A pre-existing connection with matching data should be reused """
        phone = '1112223333'
        connection1 = self.create_connection({'identity': phone})
        backend1 = connection1.backend
        contact = self.create_contact({'phone': phone,
                                       'primary_backend': backend1,
                                       'primary_connection': connection1})
        connection2 = self.create_connection({'identity': phone})
        contact.primary_backend = connection2.backend
        contact.set_primary_connection()
        contact.save()
        self.assertEqual(contact.primary_connection_id, connection2.pk)
