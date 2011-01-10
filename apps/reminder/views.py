# Create your views here.
import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rapidsms.models import Contact
from django.http import HttpResponse
from django.core import serializers
from apps.reminder.models import Group
from django.db.models.query_utils import Q


def dashboard(request):
    return render_to_response("reminder/base.html",RequestContext(request),{})



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
def contacts_table(request):
    sEcho = request.GET.get('sEcho')
    iDisplayStart = request.GET.get('iDisplayStart')
    iDisplayLength = request.GET.get('iDisplayLength')
    iColumns = request.GET.get('iColumns')
    sSearch = request.GET.get('sSearch')
    bEscapeRegex = request.GET.get('bEscapeRegex')
    
    resp = {"sEcho":sEcho}
    queryset = Contact.objects.all()
    resp.update({"iTotalRecords":queryset.count()})

    queryset = queryset.filter(Q(name__icontains=sSearch) | Q(connection__identity__icontains=sSearch) \
                        | Q(language__icontains=sSearch) | Q(groups__name__icontains=sSearch)).distinct()
    
    resp.update({"iTotalDisplayRecords":queryset.count()})
    queryset = queryset[iDisplayStart:iDisplayStart+iDisplayLength]
    aaData = []
    
    for c in queryset:
        groups = ", ".join(g.name for g in c.groups.all())
        aaData.append([c.id, c.name, c.default_connection.identity, c.language, groups])
  
    resp.update({"aaData":aaData})

    j = json.dumps(resp)
    return HttpResponse(j)
    

def groups_table(request):
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
    queryset = Group.objects.all()
    
    resp.update({"iTotalRecords":queryset.count()})
    queryset = queryset.filter(Q(name__icontains=sSearch) | Q(description__icontains=sSearch)).distinct() 
    resp.update({"iTotalDisplayRecords":queryset.count()})  
    queryset = queryset[iDisplayStart:iDisplayStart+iDisplayLength]
    aaData = []
    
    for c in queryset:
        aaData.append([c.id, c.name, c.description]);
            
    resp.update({"aaData":aaData})
    j = json.dumps(resp)
    return HttpResponse(j)
    
    
    