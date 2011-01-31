# Create your views here.
import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rapidsms.models import Contact
from django.http import HttpResponse
from django.core import serializers
from apps.reminder.models import Group
from django.db.models.query_utils import Q

from afrims.apps.utils import table
from afrims.apps.broadcast.forms import BroadcastForm



def dashboard(request):

    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            return HttpResponse('submit success with valid data')
    else:
        form = BroadcastForm()
    return render_to_response('broadcast/base.html',
                              {'form':form},
                              RequestContext(request))


def contacts_table(request):
    return table.contacts_table(request)

def groups_table(request):
    return table.groups_table(request)