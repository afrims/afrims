import datetime
import logging
import urlparse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseServerError,\
                        HttpResponseBadRequest, HttpResponseRedirect
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins

from rapidsms.models import Contact, Connection, Backend

from afrims.decorators import has_perm_or_basicauth
from afrims.apps.reminders import models as reminders
from afrims.apps.reminders.forms import NotificationForm, ReportForm
from afrims.apps.reminders.importer import parse_payload

logger = logging.getLogger('afrims.apps.reminder')


@login_required
def dashboard(request):
    today = datetime.date.today()
    appt_date = today + datetime.timedelta(weeks=1)
    form = ReportForm(request.GET or None)
    if form.is_valid():
        appt_date = form.cleaned_data['date'] or appt_date

    unconfirmed_patients = reminders.Patient.objects.unconfirmed_for_date(appt_date)
    notifications = reminders.Notification.objects.all()
    context = {
        'report_form': form,
        'notifications': notifications,
        'unconfirmed_patients': unconfirmed_patients,
        'appt_date': appt_date,
    }
    return render_to_response('reminders/dashboard.html', context,
                              RequestContext(request))


@csrf_exempt
@require_http_methods(['POST'])
@has_perm_or_basicauth('reminders.add_patientdatapayload', 'Reminders')
def receive_patient_record(request):
    ''' Accept data submissions from the the site via POST. '''
    if request.META['CONTENT_TYPE'] != 'text/xml':
        logger.warn('incoming post does not have text/xml content type')
        logger.debug(request)
    content = request.raw_post_data
    if not content:
        logger.error("No XML data appears to be attached.")
        return HttpResponseServerError("No XML data appears to be attached.")
    payload = reminders.PatientDataPayload.objects.create(raw_data=content)
    try:
        parse_payload(payload)
    except Exception as e:
        if getattr(settings, 'NOTIFY_ON_PATIENT_IMPORT_ERROR', True):
            mail_admins(subject="Patient Import Failed", message=unicode(e))
        return HttpResponseServerError(unicode(e))
    return HttpResponse("Data submitted succesfully.")


@login_required
def create_edit_notification(request, notification_id=None):
    notification = None
    if notification_id:
        notification = get_object_or_404(reminders.Notification, pk=notification_id)
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            messages.info(request, "Notification Schedule saved successfully")
            return redirect('reminders_dashboard')
    else:
        form = NotificationForm(instance=notification)
    context = {
        'form': form,
        'notification': notification,
    }
    return render_to_response('reminders/create_edit.html', context,
                              context_instance=RequestContext(request))


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(reminders.Notification, pk=notification_id)
    if request.method == 'POST':
        notification.delete()
        messages.info(request, 'Notification Schedule successfully deleted')
        return redirect('reminders_dashboard')
    context = {'notification': notification}
    return render_to_response('reminders/delete.html', context,
                              RequestContext(request))


@login_required
def report(request):
    """
    Weekly appointment reminder report.
    """
    
    
    status = request.GET.get('status', None)
    today = datetime.date.today()
    appt_date = today + datetime.timedelta(weeks=1)
    form = ReportForm(request.GET or None)
    if form.is_valid():
        appt_date = form.cleaned_data['date'] or appt_date
    confirmed_patients = reminders.Patient.objects.confirmed_for_date(appt_date)
    unconfirmed_patients = reminders.Patient.objects.unconfirmed_for_date(appt_date)

    context = {
        'report_form': form,
        'status': status,
        'appt_date': appt_date,
        'confirmed_patients': confirmed_patients,
        'unconfirmed_patients': unconfirmed_patients,
    }

    if status == 'confirmed':
        context['patients'] = context['confirmed_patients']
    elif status == 'unconfirmed':
        context['patients'] = context['unconfirmed_patients']
    if status:
        return render_to_response('reminders/small-report.html', context,
                                  RequestContext(request))
    else:
        return render_to_response('reminders/report.html', context,
                                  RequestContext(request))


@login_required
def manually_confirm(request, reminder_id):
    reminder = get_object_or_404(reminders.SentNotification, pk=reminder_id)
    if request.method == 'POST':
        redirect_to = request.POST.get('next', 'reminders_dashboard')
        try:
            netloc = urlparse.urlparse(redirect_to)[1]
        except IndexError:
            netloc = ''
        if netloc and netloc != request.get_host():
            redirect_to = 'reminders_dashboard'
        reminder.manually_confirm()
        messages.info(request, 'Patient has been confirmed manually')
        return redirect(redirect_to)
    context = {
        'reminder': reminder
    }
    return render_to_response('reminders/confirm.html', context,
                              RequestContext(request))

