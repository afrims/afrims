from django.db import models


class ContactExtra(models.Model):
    """ Abstract model to extend the RapidSMS Contact model """

    primary_backend = models.ForeignKey('rapidsms.Backend', null=True,
                                        blank=True,
                                        related_name='contact_primary')
    primary_connection = models.ForeignKey('rapidsms.Connection', null=True,
                                           blank=True,
                                           related_name='contact_primary')

    def get_or_create_connection(self):
        """ Look for a connection related to specified phone and backend """
        from rapidsms.models import Backend, Connection
        if Backend.objects.count() > 0:
            if not self.primary_backend:
                # TODO: possibly make this a setting
                self.primary_backend = Backend.objects.all()[0]
            data = {'backend': self.primary_backend,
                    'identity': self.phone}
            connection, _ = Connection.objects.get_or_create(**data)
            return connection

    def set_primary_connection(self):
        self.primary_connection = self.get_or_create_connection()
        return self.primary_connection

    class Meta:
        abstract = True
