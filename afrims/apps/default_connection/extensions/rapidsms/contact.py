from django.db import models


class ContactExtra(models.Model):
    """ Abstract model to extend the RapidSMS Contact model """

    default_backend = models.ForeignKey('rapidsms.Backend', null=True,
                                        blank=True,
                                        related_name='contact_defaults')
    default_connection = models.ForeignKey('rapidsms.Connection', null=True,
                                           blank=True,
                                           related_name='contact_defaults')

    def get_or_create_connection(self):
        """ Look for a connection related to specified phone and backend """
        from rapidsms.models import Backend, Connection
        if Backend.objects.count() > 0:
            if not self.default_backend:
                # TODO: possibly make this a setting
                self.default_backend = Backend.objects.all()[0]
            data = {'backend': self.default_backend,
                    'identity': self.phone}
            connection, _ = Connection.objects.get_or_create(**data)
            return connection

#     @property
#     def default_connection(self):
#         try:
#             return self.connection_set.filter(backend=self.default_backend)[0]
#         except IndexError:
#             return None
# 
#     def save(self, **kwargs):
#         self.name = "%s %s" % (self.first_name, self.last_name)
#         super(ContactExtra, self).save(**kwargs)

    class Meta:
        abstract = True
