from django.contrib import admin

from afrims.apps.pincode import models as pincode


class OutgoingMessageAdmin(admin.ModelAdmin):
    search_fields = ('text', 'connection', 'status', 'date_queued',
                     'date_sent')
    list_filter = ('status', 'date_queued', 'date_sent')
admin.site.register(pincode.OutgoingMessage, OutgoingMessageAdmin)
