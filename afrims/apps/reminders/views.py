from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.db.models import Q

from afrims.apps.reminders import models as reminders


def dashboard(request):
    sent_notifications = reminders.SentNotification.objects.order_by('-date_logged')
    context = {
        'sent_notifications': sent_notifications,
    }
    return render_to_response('reminders/dashboard.html', context,
                              RequestContext(request))
