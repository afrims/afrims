import datetime

from django.utils.translation import ugettext

from afrims.apps.reminders.app import RemindersApp
from afrims.apps.reminders.models import Notification

def messages(request):
    
    try:
        days = Notification.objects.order_by('?')[0].num_days
    except IndexError:
        days = 2
    date = datetime.date.today() + datetime.timedelta(days=days)
    msg = RemindersApp._notification_msg(date)
    return {
        'reminder_message': msg,
    }
