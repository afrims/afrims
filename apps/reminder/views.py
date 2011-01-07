# Create your views here.
import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rapidsms.models import Contact
from django.http import HttpResponse
from django.core import serializers
from apps.reminder.models import Group


def dashboard(request):
    return render_to_response("reminder/base.html",RequestContext(request),{})

def contacts_table(request):
    return get_table_data(request, "contacts")

def groups_table(request):
    return get_table_data(request, "group")
    
    
def get_table_data(request, type):
    """ takes a Request object and a type string (== "contacts" or "group")
    and spits back the data in a format DataTables (jquery plugin) can understand.
    """
    
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
    
    if(type=="contacts"):
        queryset = Contact.objects.all()
    elif(type=="group"):
        queryset = Group.objects.all()
    else:
        return HttpResponse("Invalid Data table type requested");
    
    resp.update({"iTotalRecords":queryset.count()})
    resp.update({"iTotalDisplayRecords":queryset.count()})
    queryset = queryset[iDisplayStart:iDisplayStart+iDisplayLength]
    aaData = []
    
    for c in queryset:
        if(type=="contacts"):
            groups = ", ".join(g.name for g in c.groups.all())
            aaData.append([c.id, c.name, c.default_connection.identity, c.language, groups])
        elif(type=="group"):
            aaData.append([c.id, c.name, c.description]);
            
    resp.update({"aaData":aaData})
    j = json.dumps(resp)
    return HttpResponse(j)
    