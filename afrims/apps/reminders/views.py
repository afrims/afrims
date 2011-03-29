import logging

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

from rapidsms.models import Contact, Connection, Backend

from afrims.decorators import has_perm_or_basicauth
from afrims.apps.reminders import models as reminders
from afrims.apps.reminders.forms import NotificationForm
from afrims.apps.reminders.importer import parse_payload

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
    notifications = reminders.Notification.objects.all()
    context = {
        'notifications': notifications,
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
        'group': notification,
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
