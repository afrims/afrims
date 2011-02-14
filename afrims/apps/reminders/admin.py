from django.contrib import admin

from afrims.apps.reminders import models as reminders


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('num_days',)
    search_fields = ('num_days',)
admin.site.register(reminders.Notification, NotificationAdmin)
