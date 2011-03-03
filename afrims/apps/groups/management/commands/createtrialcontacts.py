import datetime

from django.core.management.base import NoArgsCommand

from rapidsms.models import Contact

from afrims.apps.reminders.models import Patient


class Command(NoArgsCommand):
    """ Generate a few thousand trial contact records """
    requires_model_validation = True
    prefix = 'Dummy'
    
    def handle_noargs(self, **options):
        phone_number = 1111111111
        Contact.objects.filter(name__startswith=self.prefix).delete()
        for i in xrange(100):
            name = '%s Contact %d' % (self.prefix, i)
            contact = Contact.objects.create(name=name)
            if (i % 2) == 0:
                phone_number += 1
                subject_number = 'T{0:0>4}'.format(i)
                Patient.objects.create(subject_number=subject_number,
                                       date_enrolled=datetime.date.today(),
                                       mobile_number=phone_number,
                                       contact=contact)
                contact.name = subject_number
                contact.save()
