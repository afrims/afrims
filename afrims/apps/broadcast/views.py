import logging

from django.db import transaction
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from afrims.apps.broadcast.forms import BroadcastForm


@login_required
@transaction.commit_on_success
def send_message(request):
    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            broadcast = form.save()
            messages.info(request, 'Message queued for delivery')
            return HttpResponseRedirect(reverse('send-message'))
    else:
        form = BroadcastForm()

    context = {
        'form': form,
    }
    return render_to_response('broadcast/send_message.html', context,
                              RequestContext(request))

