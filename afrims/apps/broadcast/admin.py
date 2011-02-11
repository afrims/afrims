from django.contrib import admin

from afrims.apps.broadcast import models as broadcast


class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_created', 'date_last_notified',
                    'date_next_notified')
    list_filter = ('date_created', 'date_last_notified')
    search_fields = ('body',)
    ordering = ('-date_last_notified',)

admin.site.register(broadcast.Broadcast, BroadcastAdmin)


class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'date_created', 'date_sent')
    list_filter = ('date_created', 'date_sent')
    ordering = ('-date_created',)

admin.site.register(broadcast.BroadcastMessage, BroadcastMessageAdmin)

