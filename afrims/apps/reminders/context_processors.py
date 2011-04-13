import datetime

from django.utils.translation import ugettext

from afrims.apps.reminders.app import RemindersApp
from afrims.apps.reminders.models import Notification

def messages(request):
    try:
        days = Notification.objects.order_by('-num_days')[0].num_days
    except IndexError:
        days = 1
    date = datetime.datetime.today() + datetime.timedelta(days=days)
    msg = ugettext(RemindersApp.future_appt_msg)
    msg = msg.format(days=days, date=date.strftime(RemindersApp.date_format),
                     confirm_response=RemindersApp.conf_keyword)
    return {
        'future_appt_msg': msg,
    }
