import logging

from django.db import models
from django.conf import settings


logger = logging.getLogger('afrims.apps.default_connection')


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
        """ Determine needed backend and return associated connection """
        from rapidsms.models import Backend
        if not backend_name and hasattr(settings, 'PRIMARY_BACKEND'):
            backend_name = settings.PRIMARY_BACKEND
            logger.debug('found {0} in settings'.format(backend_name))
        if self.primary_backend_id:
            backend = self.primary_backend
            logger.debug('using contact backend: {0}'.format(backend))
        elif backend_name:
            backend = Backend.objects.get(name=backend_name)
            logger.debug('using backend: {0}'.format(backend))
        else:
            backend = Backend.objects.all()[0]
            logger.debug('using random backend: {0}'.format(backend))
        connection = self.get_or_create_connection(backend=backend)
        if not connection.contact:
            msg = 'associating connection ({0}) to contact ({1})'
            logger.debug(msg.format(connection, self))
            connection.contact = self
            connection.save()
        return connection

    @property
    def default_connection(self):
        """ Override default_connection to return primary connection """
        return self.get_primary_connection()

    class Meta:
        abstract = True
