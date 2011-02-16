from django.db import models

from rapidsms import models as rapidsms


class Notification(models.Model):
    '''
    An appointment notifications to be sent to trial participants.
    '''
    num_days = models.IntegerField(help_text='Number of days before the '
                                   'scheduled appointment to send a reminder.')

    def __unicode__(self):
        return u'{0} day'.format(self.num_days)


class SentNotification(models.Model):
    '''
    A notification sent to a trial participant.
    '''
    notification = models.ForeignKey(Notification,
                                    related_name='sent_notifications')
    recipient = models.ForeignKey(rapidsms.Contact,
                                  related_name='sent_notifications')
    date_logged = models.DateTimeField()
    message = models.CharField(max_length=160)
    
    def __unicode__(self):
        return u'{notification} sent to {recipient} on {date}'.format(
                                        notification=self.notification,
                                        recipient=self.recipient,
                                        date=self.date_logged)


class PatientDataPayload(models.Model):
    '''
        Dumping area for incoming patient data xml snippets
    '''
    raw_data = models.TextField()
    submit_date = models.DateTimeField()

    def __unicode__(self):
        return u'Raw Data Payload, submitted on: {date}'.format(date=self.submit_date)


class Patient(models.Model):
    raw_data = models.ForeignKey(PatientDataPayload, null=True, blank=True) #we might create Patients manually
    subject_number = models.CharField(max_length=20)
    date_enrolled = models.DateField()
    mobile_number = models.CharField(max_length=30)
    pin = models.CharField(max_length=4, blank=True,help_text="A 4-digit pin code for sms authentication workflows.")
    next_visit = models.DateField(blank=True,null=True)
    contact = models.ForeignKey(rapidsms.Contact, null=True, blank=True)


    def __unicode__(self):
        return u'Patient, Subject ID:{id}, Enrollment Date:{date_enrolled}'.format(id=self.subject_number,
                                                  date_enrolled=self.date_enrolled)
