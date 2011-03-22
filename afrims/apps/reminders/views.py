import logging
from datetime import datetime

from lxml import etree
from lxml.etree import XMLSyntaxError

from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseServerError,\
                        HttpResponseBadRequest, HttpResponseRedirect
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from rapidsms.models import Contact, Connection, Backend

from afrims.decorators import has_perm_or_basicauth
from afrims.apps.groups.models import Group
from afrims.apps.reminders import models as reminders
from afrims.apps.reminders.forms import NotificationFormset

logger = logging.getLogger('afrims.apps.reminder')



@login_required
def dashboard(request):
    queued = reminders.SentNotification.objects.filter(status='queued')
    sent = reminders.SentNotification.objects.filter(status='sent')
    confirmed = reminders.SentNotification.objects.filter(status='confirmed')
    reminder_report = {
        'queued': queued.count(),
        'sent': sent.count(),
        'confirmed': confirmed.count(),
    }
    if request.method == 'POST':
        notification_formset = NotificationFormset(request.POST)
        if notification_formset.is_valid():
            notifications = notification_formset.save()
            return HttpResponseRedirect(reverse('reminders_dashboard'))
    else:
        notification_formset = NotificationFormset()
    context = {
        'reminder_report': reminder_report,
        'notification_formset': notification_formset,
    }
    return render_to_response('reminders/dashboard.html', context,
                              RequestContext(request))


@csrf_exempt
@require_http_methods(['POST'])
@has_perm_or_basicauth('reminders.add_patientdatapayload', 'Reminders')
@transaction.commit_on_success
def receive_patient_record(request):
    '''
    Accept data submissions from the the site via POST.
    '''
    if request.META['CONTENT_TYPE'] != 'text/xml':
        logger.warn('incoming post does not have text/xml content type')
        logger.debug(request)


    content = request.raw_post_data
    if not content:
        return HttpResponseServerError("No XML data appears to be attached.")

    #save the raw data just in case
    raw_data = reminders.PatientDataPayload(raw_data=content,
                                            submit_date=datetime.now())
    raw_data.save()
    
    try:
        root = etree.fromstring(content)
        for patient in root.iter("Table"):

            if not create_or_update_patient_model(patient,raw_data): #includes validation
                HttpResponseBadRequest("XML Parsing Error")


    except XMLSyntaxError as e:
        return HttpResponseBadRequest("XML Syntax Error %s" % str(e))


    return HttpResponse("Data submitted succesfully.")


def create_or_update_patient_model(patient, raw_data_entry):
    '''
    Creates a new patient_model entry (or updates if exists), also creating a Contact for that patient as needed.
    Returns False if there was an error parsing the xml patient data (the XML syntax is correct
    but we don't understand it or there was some other error).
    Returns True upon succesfully creating a Patient and related Contact
    '''
    logger.debug(etree.tostring(patient))

    subject_number = None
    enroll_date = None
    mobile_number = None
    pin = None
    next_visit = None

    for data in patient.getchildren():
        if data.tag == "Subject_Number": subject_number = data.text
        if data.tag == "Date_Enrolled": enroll_date = datetime.strptime(data.text,'%b  %d %Y ')
        if data.tag == "Mobile_Number": mobile_number = clean_number(data.text)
        if data.tag == "Pin_Code": pin = (data.text if data.text else '')  #in case we opt to not use pin codes
        if data.tag == "Next_Visit": next_visit = datetime.strptime(data.text,'%b  %d %Y ')

    if not (subject_number and enroll_date and mobile_number and pin):
        return False #something is wrong with our parsing.
    (patient_model, new_patient) = reminders.Patient.objects.get_or_create(
                            subject_number=subject_number,
                            date_enrolled=enroll_date,
                            )
    #these values can all change over time so we update them
    patient_model.pin=pin
    patient_model.mobile_number=mobile_number
    patient_model.raw_data=raw_data_entry
    patient_model.next_visit=next_visit

    contact = None
    try:
        contact = Contact.objects.get(name=subject_number, connection__identity=mobile_number) #assuming each Contact's name is their patient ID   
    except ObjectDoesNotExist:
        #create a new Contact
        (group, group_created) = Group.objects.get_or_create(name=settings.DEFAULT_SUBJECT_GROUP_NAME)
        contact = Contact(name=subject_number)
        contact.save()
        contact.groups.add(group)
        contact.save()
        backend = None
        try:
            backend = Backend.objects.get(name=settings.DEFAULT_BACKEND_NAME)
            (conn, new_conn) = Connection.objects.get_or_create(identity=mobile_number,backend=backend)
            conn.contact=contact
            conn.save()
        except ObjectDoesNotExist:
            logging.error("Can't find Backend specified by DEFAULT_BACKEND_NAME in settings!")
            return False

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
