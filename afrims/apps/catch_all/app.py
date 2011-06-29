import logging

from django.core.exceptions import ObjectDoesNotExist

from rapidsms.apps.base import AppBase
from afrims.apps.reminders.models import Patient

# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s

class CatchAllApp(AppBase):
    """ RapidSMS app to reply to unhandled messages """

    # Which message we send when we don't recognize the message
    # depends on who sent it.
    patient_template = _("""Thank you for contacting us. Please reply with 2 to be """ \
                         """called back within 2 days.""")
    non_patient_template = _("""Sorry, that message was not recognized""")

    def default(self, msg):
        """ If we reach the default phase here, respond with an appropriate
        message"""

        contact = msg.connection.contact

        # are they a patient?
        try:
            patient = Patient.objects.get(contact=contact)
            # yes
            msg.respond(self.patient_template)
        except ObjectDoesNotExist, e:
            # no
            msg.respond(self.non_patient_template)
        except e:
            # should not happen, would probably mean multiple
            # patients with the same contact
            logging.error(e)
            return False

        return True
