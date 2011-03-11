from django.db import models
from django.conf import settings


class ContactExtra(models.Model):
    """ Abstract model to extend the RapidSMS Contact model """

    primary_backend = models.ForeignKey('rapidsms.Backend',
                                        null=True, blank=True,
                                        related_name='contact_primary')

    def get_or_create_connection(self, backend):
        """ Look for a connection related to specified phone and backend """
        from rapidsms.models import Connection
        data = {'backend': backend, 'identity': self.phone}
        connection, _ = Connection.objects.get_or_create(**data)
        return connection

    def get_primary_connection(self, backend_name=None):
        """ Override Contact's default_connection """
        from rapidsms.models import Backend
        if not backend_name and hasattr(settings, 'PRIMARY_BACKEND'):
            backend_name = settings.PRIMARY_BACKEND
        if self.primary_backend_id:
            backend = self.primary_backend
        elif backend_name:
            backend = Backend.objects.get(name=backend_name)
        else:
            backend = Backend.objects.all()[0]
        connection = self.get_or_create_connection(backend=backend)
        if not connection.contact:
            connection.contact = self
            connection.save()
        return connection

    class Meta:
        abstract = True
