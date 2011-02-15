from django.contrib import admin

from afrims.apps.reminders import models as reminders


class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('num_days',)
admin.site.register(reminders.Notification, NotificationAdmin)


class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ('date_logged', 'recipient', 'notification', 'message')
    search_fields = ('date_logged', 'recipient', 'notification', 'message')
    list_filter = ('date_logged', 'notification')
admin.site.register(reminders.SentNotification, SentNotificationAdmin)
