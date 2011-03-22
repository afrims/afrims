import logging
from datetime import datetime
from lxml import etree

from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings

from rapidsms.models import Contact, Connection, Backend

from afrims.apps.reminders import models as reminders
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

    subject_number = None
    enroll_date = None
    mobile_number = None
    pin = None
    next_visit = None

    for data in node.getchildren():
        if data.tag == "Subject_Number": subject_number = data.text
        if data.tag == "Date_Enrolled": enroll_date = datetime.strptime(data.text,'%b  %d %Y ')
        if data.tag == "Mobile_Number": mobile_number = clean_number(data.text)
        if data.tag == "Pin_Code": pin = (data.text if data.text else '')  #in case we opt to not use pin codes
        if data.tag == "Next_Visit": next_visit = datetime.strptime(data.text,'%b  %d %Y ')

    if not (subject_number and enroll_date and mobile_number and pin):
        logger.warning('Missing data, exiting...')
        return False #something is wrong with our parsing.
    (patient_model, new_patient) = reminders.Patient.objects.get_or_create(
                            subject_number=subject_number,
                            date_enrolled=enroll_date,
                            )
    logger.debug('Using patient ID {0}'.format(patient_model.pk))
    #these values can all change over time so we update them
    patient_model.pin=pin
    patient_model.mobile_number=mobile_number
    patient_model.raw_data=payload
    patient_model.next_visit=next_visit

    contact = None
    try:
        contact = Contact.objects.get(name=subject_number, connection__identity=mobile_number) #assuming each Contact's name is their patient ID   
    except Contact.DoesNotExist:
        #create a new Contact
        (group, group_created) = Group.objects.get_or_create(name=settings.DEFAULT_SUBJECT_GROUP_NAME)
        contact = Contact(name=subject_number)
        contact.save()
        contact.groups.add(group)

    patient_model.contact = contact
    patient_model.save()
    return True


def clean_number(raw_number):
    '''
        cleans submitted phone numbers
    '''
    num = raw_number.replace(')','')
    num = num.replace('(','')
    num = num.replace('-','')
    num = num.strip()
    return num
