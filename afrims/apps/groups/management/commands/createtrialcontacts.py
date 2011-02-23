from django.core.management.base import NoArgsCommand

from rapidsms.models import Contact


class Command(NoArgsCommand):
    """ Generate a few thousand trial contact records """
    requires_model_validation = True
    prefix = 'Trial ID'

    def handle_noargs(self, **options):
        Contact.objects.filter(name__startswith=self.prefix).delete()
        for i in xrange(3000):
            name = '%s %d' % (self.prefix, i)
            Contact.objects.create(name=name)
