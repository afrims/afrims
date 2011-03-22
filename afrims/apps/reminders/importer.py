import logging
from datetime import datetime
from lxml import etree

from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings

from rapidsms.models import Contact, Connection, Backend

from afrims.apps.reminders import models as reminders
from afrims.apps.reminders.forms import PatientForm
from afrims.apps.groups.models import Group


logger = logging.getLogger('afrims.apps.reminders.importer')


@transaction.commit_on_success
def parse_payload(payload):
    """ Parse entire XML payload sent from external database """
    try:
        root = etree.fromstring(payload.raw_data)
        for patient in root.iter("Table"):
            parse_patient(patient, payload)
    except etree.XMLSyntaxError as e:
        logger.exception(e)
        raise ValidationError("XML Syntax Error %s" % str(e))
    except ValidationError as e:
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise ValidationError(e)


def parse_patient(node, payload):
    '''
    Creates a new patient_model entry (or updates if exists), also creating a Contact for that patient as needed.
    Returns False if there was an error parsing the xml patient data (the XML syntax is correct
    but we don't understand it or there was some other error).
    Returns True upon succesfully creating a Patient and related Contact
    '''
    logger.debug('Creating patient...')
    logger.debug(etree.tostring(node, pretty_print=True))
    # mapping of XML tags to Patient model fields
    valid_field_names = {
        "Subject_Number": 'subject_number',
        "Date_Enrolled": 'date_enrolled',
        "Mobile_Number": 'mobile_number',
        "Pin_Code": 'pin',
        "Next_Visit": 'next_visit',
    }
    # convert XML structure into POST-like dictionary
    data = {}
    for field in node.getchildren():
        key = valid_field_names.get(field.tag, field.tag)
        data[key] = field.text
    logger.debug(data)
    # look up patient by subject number to see if this is an update
    instance = None
    if 'subject_number' in data:
        patient_kwargs = {'subject_number': data['subject_number']}
        try:
            instance = reminders.Patient.objects.get(**patient_kwargs)
            logger.debug("Found patient {0}".format(instance.subject_number))
        except reminders.Patient.DoesNotExist:
            number = patient_kwargs['subject_number']
            logger.debug("Patient {0} doesn't exist".format(number))
    # construct model form and see if data is valid
    form = PatientForm(data, instance=instance)
    if form.is_valid():
        patient = form.save(payload=payload)
    else:
        logger.debug('Patient data is invalid')
        errors = dict((k, v[0]) for k, v in form.errors.items())
        raise ValidationError(errors)

