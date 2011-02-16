from django.contrib import admin

from afrims.apps.reminders import models as reminders


class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('num_days',)
admin.site.register(reminders.Notification, NotificationAdmin)


class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ('date_queued', 'status', 'recipient', 'notification',
                    'date_delivered', 'date_confirmed', 'message')
    search_fields = ('date_queued', 'status', 'recipient', 'notification',
                     'message')
    list_filter = ('status', 'notification', 'date_queued', 'date_delivered',
                   'date_confirmed')
admin.site.register(reminders.SentNotification, SentNotificationAdmin)
