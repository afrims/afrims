# Create your views here.
import json

from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rapidsms.models import Contact
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from apps.reminder.models import Group
from django.db.models.query_utils import Q

from afrims.apps.utils import table
from afrims.apps.broadcast.forms import BroadcastForm
from django.core.context_processors import csrf
from django.db.models import Q
from apps.broadcast.models import BroadcastMessage
from rapidsms.models import Connection
from rapidsms.models import Backend
from apps.broadcast import utils
from django.core.exceptions import ObjectDoesNotExist

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

''' Select whether to show the Contacts selection table in the broadcast UI tab '''
SHOW_CONTACTS_SELECTION = 'false' #use JavaScript true/false syntax!

def dashboard(request):

    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            sender_num = form.cleaned_data['sender_number']
            contacts_field = form.cleaned_data['contacts']
            groups_field = form.cleaned_data['groups']
            msg_txt = form.cleaned_data['message_text']

            recipients = Contact.objects.filter(id__in=contacts_field)
            groups_recipients = Contact.objects.filter(groups__id__in=groups_field)
            recipients = (recipients | groups_recipients).distinct()

            bm = make_broadcast_entry(sender_num,msg_txt,recipients)
            send_broadcast(bm)

            print contacts
            return HttpResponseRedirect('sent/')

    else:
        form = BroadcastForm()

    c = {'form':form, 'show_contacts':SHOW_CONTACTS_SELECTION}
    c.update(csrf(request))
    return render_to_response('broadcast/base.html',
                              c,
                              RequestContext(request))


def make_broadcast_entry(sender_identity,text,recipients):
    '''
    Creates a BroadcastMessage model entry and returns it
    '''
    sender = _get_or_create_connection(sender_identity)
    bm = BroadcastMessage(connection=sender,text=text)
    bm.save()
    bm.recipients = recipients
    bm.save()

    return bm

def _get_or_create_connection(identity):
    '''
    Get's or creates a connection to be stored in the BroadcastMessage Model
    '''
    try:
        conn = Connection.objects.get(identity=identity)
    except ObjectDoesNotExist:
        sender_backend = Backend.objects.filter(name=settings.BROADCAST_SENDER_BACKEND)
        if not sender_backend:
            raise Exception('Broadcast sender backend not found: %s' % settings.BROADCAST_SENDER_BACKEND)
        sender_backend = sender_backend[0]
        conn = Connection(backend=sender_backend, identity=identity)
        conn.save()

    return conn

def send_broadcast(broadcast_msg):
    bm = broadcast_msg
    ident_list = ''

    for recipient in bm.recipients.all():
        if(recipient.default_connection):
            ident_list += 'recipient.default_connection.identity'+','
        else:
            logger.warn('Unable to broadcast to recipient %s: No Connection Found' % recipient.name)
    ident_list.strip(',')
    utils.send_broadcast_message(ident=bm.connection.identity,text=bm.text,recipients=ident_list)







def contacts_table(request):
    return table.contacts_table(request)

def groups_table(request):
    return table.groups_table(request)

def message_sent(request):
    return render_to_response('layout.html',
                              {},
                              RequestContext(request))