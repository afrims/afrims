from django.utils import simplejson as json
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.context import RequestContext

from afrims.apps.test_messager.forms import MessageForm


class JsonResponse(HttpResponse):
    """ Simple HttpResponse extension that converts data into JSON """
    def __init__(self, content='', mimetype=None, status=None,
                 content_type=None):
        content = json.dumps(content)
        mimetype = "application/json"
        super(JsonResponse, self).__init__(content, mimetype, status,
                                           content_type)


def message_form(request):
    """ AJAX view for rendering test messager form and sending messages """
    if request.POST:
        form = MessageForm(request.POST)
        if form.is_valid():
            try:
                status = form.save()
            except Exception, e:
                import traceback
                traceback.print_exc()
    else:
        initial = {}
        message = request.GET.get('message', '')
        if message:
            initial = {'message': message}
        form = MessageForm(initial=initial)   
    form = render_to_string('test_messager/form.html', {'form': form},
                            RequestContext(request))
    content = {
        'form': form,
    }
    return JsonResponse(content)

