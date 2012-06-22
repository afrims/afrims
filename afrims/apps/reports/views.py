import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.views.generic.simple import direct_to_template as render

from rapidsms.contrib.messagelog.models import Message
from rapidsms.models import Contact

from afrims.apps.reminders.models import SentNotification


@login_required
@permission_required('groups.can_use_dashboard_tab',login_url='/access_denied/')
def dashboard(request):
    "Reporting dashboard."
    today = datetime.date.today()
    context = {}
    to_date = {
        'messages': messages_by_direction(),
        'users': user_stats(),
        'appointments': appointment_stats(),
        'reminders': reminder_stats(),
    }
    this_month = {
        'messages': messages_by_direction(day=today),
        'users': user_stats(day=today),
        'patient_messages': messages_by_direction(day=today, filters={'contact__in': Contact.objects.filter(patient__isnull=False)}),
        'staff_messages': messages_by_direction(day=today, filters={'contact__in': Contact.objects.filter(patient__isnull=True)}),
        'appointments': appointment_stats(day=today),
        'reminders': reminder_stats(day=today),
    }
    prev_month = today - datetime.timedelta(days=today.day + 1)
    last_month = {
        'appointments': appointment_stats(day=prev_month),
        'reminders': reminder_stats(day=prev_month),
    }
    context['to_date'] = to_date
    context['this_month'] = this_month
    context['last_month'] = last_month
    return render(request, 'reports/dashboard.html', context)


def transform(x, y):
    "Transform the lists from the values query to a flat dictionary."
    direction = {'I': 'incoming', 'O': 'outgoing'}.get(y['direction'], None)
    if direction:
        x[direction] = y['count']
    return x


def messages_by_direction(day=None, filters=None):
    "Return a dictionary of filtered messages in the given range by count."
    date_q  = Q()
    if day is not None:
        date_q = Q(date__month=day.month, date__year=day.year)
    filter_q = Q()
    if filters is not None:
        filter_q = Q(**filters)
    messages = Message.objects.filter(date_q, filter_q).annotate(count=Count('id')).values('direction', 'count')
    return reduce(transform, messages, {})


def appointment_stats(day=None):
    "Confirmed, total and % confirmed appointments for a given month or to date."
    confirmed = count_appointments(day=day, filters={'status__in': ['confirmed', 'manual']})
    total = count_appointments(day=day)
    percent = float(confirmed) / total * 100 if total else 0.0
    return {'confirmed': confirmed, 'total': total, 'percent': percent}


def count_appointments(day=None, filters=None):
    "The number of appointements matching a set of filters."
    date_q  = Q()
    if day is not None:
        date_q = Q(appt_date__month=day.month, appt_date__year=day.year)
    filter_q = Q()
    if filters is not None:
        filter_q = Q(**filters)
    return SentNotification.objects.filter(
        date_q, filter_q, recipient__patient__isnull=False
    ).values('appt_date', 'recipient').distinct().count()


def reminder_stats(day=None):
    "Confirmed, total and % confirmed reminders for a given month or to date."
    confirmed = count_reminders(day=day, filters={'status__in': ['confirmed', 'manual']})
    total = count_reminders(day=day)
    percent = float(confirmed) / total * 100 if total else 0.0
    return {'confirmed': confirmed, 'total': total, 'percent': percent}


def count_reminders(day=None, filters=None):
    "The number of reminders matching a set of filters."
    date_q  = Q()
    if day is not None:
        date_q = Q(appt_date__month=day.month, appt_date__year=day.year)
    filter_q = Q()
    if filters is not None:
        filter_q = Q(**filters)
    return SentNotification.objects.filter(date_q, filter_q).distinct().count()


def user_stats(day=None):
    "Patients, staff and total users. If day is given filters active users from that date."
    patients = count_users(filters={'patient__isnull': False})
    staff = count_users(filters={'patient__isnull': True})
    total = patients + staff
    return {'patients': patients, 'total': total, 'staff': staff}


def count_users(day=None, filters=None):
    "The number of users matching a set of filters. If day is given filters active users."
    date_q  = Q()
    if day is not None:
        ninety_days_ago = day - datetime.timedelta(days=90)
        date_q = Q(message__date__range=(ninety_days_ago, day))
    filter_q = Q()
    if filters is not None:
        filter_q = Q(**filters)
    return Contact.objects.filter(date_q, filter_q).distinct().count()
