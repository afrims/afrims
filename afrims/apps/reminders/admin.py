from django.contrib import admin

from afrims.apps.reminders import models as reminders


class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('num_days',)
admin.site.register(reminders.Notification, NotificationAdmin)


class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ('date_queued', 'status', 'recipient', 'notification',
                    'date_sent', 'date_confirmed', 'message')
    search_fields = ('date_queued', 'status', 'recipient', 'notification',
                     'message')
    list_filter = ('status', 'notification', 'date_queued', 'date_sent',
                   'date_confirmed')
admin.site.register(reminders.SentNotification, SentNotificationAdmin)


class PatientAdmin(admin.ModelAdmin):
    list_display = ('subject_number', 'date_enrolled', 'next_visit',
                    'mobile_number', 'pin', 'contact')
    list_filter = ('next_visit',)
    date_hierarchy = 'date_enrolled'
    ordering = ('-date_enrolled',)
    search_fields = ('subject_number', 'pin', 'mobile_number')
admin.site.register(reminders.Patient, PatientAdmin)

admin.site.register(reminders.PatientDataPayload)
