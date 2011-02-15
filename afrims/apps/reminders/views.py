from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from afrims.apps.reminders import models as reminders


@login_required
def dashboard(request):
    queued = reminders.SentNotification.objects.filter(status='queued')
    delivered = reminders.SentNotification.objects.filter(status='delivered')
    confirmed = reminders.SentNotification.objects.filter(status='confirmed')
    reminder_report = {
        'queued': queued.count(),
        'delivered': delivered.count(),
        'confirmed': confirmed.count(),
    }
    context = {
        'reminder_report': reminder_report,
    }
    return render_to_response('reminders/dashboard.html', context,
                              RequestContext(request))
