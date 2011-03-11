from django.contrib import admin
from afrims.apps.groups.models import Group, ForwardingRule

admin.site.register(Group)

admin.site.register(ForwardingRule)
