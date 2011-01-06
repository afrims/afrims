# Create your views here.
import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rapidsms.models import Contact
from django.http import HttpResponse
from django.core import serializers


def dashboard(request):
    return render_to_response("reminder/base.html",RequestContext(request),{})

def contacts_table(request):
    sEcho = request.GET.get('sEcho')
    iDisplayStart = request.GET.get('iDisplayStart')
    iDisplayLength = request.GET.get('iDisplayLength')
    iColumns = request.GET.get('iColumns')
    sSearch = request.GET.get('sSearch')
    bEscapeRegex = request.GET.get('bEscapeRegex')
    
#    Example response:
#{
#    "sEcho": 3,
#    "iTotalRecords": 57,
#    "iTotalDisplayRecords": 57,
#    "aaData": [
#        [
#            "Gecko",
#            "Firefox 1.0",
#            "Win 98+ / OSX.2+",
#            "1.7",
#            "A"
#        ],
#        [
#            "Gecko",
#            "Firefox 1.5",
#            "Win 98+ / OSX.2+",
#            "1.8",
#            "A"
#        ],
#        ...
#    ] 
#}
    
    resp = {"sEcho":sEcho}
    
    queryset = Contact.objects.all();
    
    resp.update({"iTotalRecords":queryset.count()})
    resp.update({"iTotalDisplayRecords":queryset.count()})
    aaData = []
    
    for c in queryset:
        aaData.append([c.id, c.name, c.default_connection.identity, c.language])
    resp.update({"aaData":aaData})
    j = json.dumps(resp)
    return HttpResponse(j)
    