from django.contrib import admin

from afrims.apps.pincode import models as pincode


class OutgoingMessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'connection', 'status', 'date_queued',
                     'date_sent')
    list_filter = ('status', 'date_queued', 'date_sent')
    search_fields = ('text', 'status',)
admin.site.register(pincode.OutgoingMessage, OutgoingMessageAdmin)
