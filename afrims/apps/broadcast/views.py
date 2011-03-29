from django.db import transaction
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404

from afrims.apps.broadcast.forms import BroadcastForm, ForwardingRuleForm
from afrims.apps.broadcast.models import Broadcast, BroadcastMessage, ForwardingRule


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
    context = {
        'rules': ForwardingRule.objects.all(),
    }
    return render_to_response('broadcast/forwarding.html', context,
                              RequestContext(request))


@login_required
def create_edit_rule(request, rule_id=None):
    rule = None
    if rule_id:
        rule = get_object_or_404(ForwardingRule, pk=rule_id)
    if request.method == 'POST':
        form = ForwardingRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.info(request, "Forwarding Rule saved successfully")
            return redirect('broadcast-forwarding')
    else:
        form = ForwardingRuleForm(instance=rule)
    context = {
        'form': form,
        'rule': rule,
    }
    return render_to_response('broadcast/create_edit_rule.html', context,
                              context_instance=RequestContext(request))


@login_required
def delete_rule(request, rule_id):
    rule = get_object_or_404(ForwardingRule, pk=rule_id)
    if request.method == 'POST':
        rule.delete()
        messages.info(request, 'Forwarding Rule successfully deleted')
        return redirect('broadcast-forwarding')
    context = {'rule': rule}
    return render_to_response('broadcast/delete_rule.html', context,
                              RequestContext(request))

