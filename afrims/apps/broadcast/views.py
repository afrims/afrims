from django.db import transaction
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404

from afrims.apps.broadcast.forms import BroadcastForm, ForwardingRuleFormset
from afrims.apps.broadcast.models import Broadcast, BroadcastMessage


@login_required
@transaction.commit_on_success
def send_message(request, broadcast_id=None):
    if broadcast_id:
        broadcast = get_object_or_404(Broadcast, pk=broadcast_id)
    else:
        broadcast = None
    if request.method == 'POST':
        form = BroadcastForm(request.POST, instance=broadcast)
        if form.is_valid():
            broadcast = form.save()
            if broadcast_id:
                info = 'Broadcast successfully saved'
            else:
                info = 'Message queued for delivery'
            messages.info(request, info)
            return HttpResponseRedirect(reverse('broadcast-schedule'))
    else:
        form = BroadcastForm(instance=broadcast)
    broadcasts = Broadcast.objects.exclude(schedule_frequency__isnull=True)
    context = {
        'form': form,
        'broadcasts': broadcasts.order_by('date'),
    }
    return render_to_response('broadcast/send_message.html', context,
                              RequestContext(request))


@login_required
@transaction.commit_on_success
def delete_broadcast(request, broadcast_id):
    broadcast = get_object_or_404(Broadcast, pk=broadcast_id)
    if request.method == 'POST':
        # disable broadcast to preserve any foreign keys
        broadcast.schedule_frequency = None
        broadcast.save()
        messages.info(request, 'Broadcast successfully deleted')
        return HttpResponseRedirect(reverse('broadcast-schedule'))
    context = {'broadcast': broadcast}
    return render_to_response('broadcast/delete.html', context,
                              RequestContext(request))


@login_required
def schedule(request):
    broadcasts = Broadcast.objects.exclude(schedule_frequency__isnull=True)
    broadcasts = broadcasts.annotate(recipients=Count('groups__contacts'))
    context = {
        'broadcasts': broadcasts.order_by('date'),
    }
    return render_to_response('broadcast/schedule.html', context,
                              RequestContext(request))


@login_required
def list_messages(request):
    messages = BroadcastMessage.objects.select_related()
    context = {
        'broadcast_messages': messages,
    }
    return render_to_response('broadcast/messages.html', context,
                              RequestContext(request))


@login_required
def forwarding(request):
    if request.method == 'POST':
        formset = ForwardingRuleFormset(request.POST)
        if formset.is_valid():
            forwarding_rules = formset.save()
            return HttpResponseRedirect(reverse('broadcast-forwarding'))
    else:
        formset = ForwardingRuleFormset()
    context = {
        'formset': formset,
    }
    return render_to_response('broadcast/forwarding.html', context,
                              RequestContext(request))
