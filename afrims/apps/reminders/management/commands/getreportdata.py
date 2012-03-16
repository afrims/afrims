import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models.aggregates import Avg
from rapidsms.contrib.messagelog.models import Message
from afrims.apps.broadcast.models import BroadcastMessage
from afrims.apps.reminders.models import SentNotification, Notification, PatientAppointment
from afrims.apps.broadcast.views import usage_report_context
from rapidsms.models import Contact
from afrims.apps.utils.odict import odict

import calendar
import pprint
class Command(BaseCommand):
    args = "<report_year report_month report_day>"
    help = "Specify a report start date (optional) to generate a report"
    def populateAppointments(self):
        def isConfirmed(status):
            return status == 'confirmed' or status == 'manual'

        def numNotifications(appt):
            count = 0.0
            activity = ['sent','confirmed', 'manual','error']
            if activity.__contains__(appt.confirmed_0day):
                count += 1.0
            if activity.__contains__(appt.confirmed_4day):
                count += 1.0
            if activity.__contains__(appt.confirmed_5day):
                count += 1.0
            return str(count)

        def numConfirmations(appt):
            count = 0
            activity = ['confirmed', 'manual']
            if activity.__contains__(appt.confirmed_0day):
                count += 1
            if activity.__contains__(appt.confirmed_4day):
                count += 1
            if activity.__contains__(appt.confirmed_5day):
                count += 1
            return str(count)


        SN = SentNotification.objects.all()
        for sentnote in SN:
            patient = sentnote.recipient.patient_set.all()
            if patient.count() == 0:
                continue
            else:
                patient = patient[0]
            (appt, created) = PatientAppointment.objects.get_or_create(appt_date = sentnote.appt_date,
                patient=patient)

            if created:
                appt.confirmed = False #mark it as unconfirmed initially and alter accordingly below.

            if sentnote.notification.num_days == 0:
                appt.confirmed_0day = sentnote.status
            elif sentnote.notification.num_days == 4:
                appt.confirmed_4day = sentnote.status
            elif sentnote.notification.num_days == 5:
                appt.confirmed_5day = sentnote.status
            else:
                print "Don't know what notification this is %s - %s" % (sentnote.notification, sentnote.notification.num_days)

            status_0day = appt.confirmed_0day
            status_4day = appt.confirmed_4day
            status_5day = appt.confirmed_5day
            if isConfirmed(status_0day) or isConfirmed(status_4day) or isConfirmed(status_5day):
                appt.confirmed = True

            appt.avg_num_notifications = numNotifications(appt)
            appt.num_confirmations = numConfirmations(appt)
            appt.save()

    def handle(self, *args, **options):
        if len(args) > 0:
            today = datetime.date(year=int(args[0]), month=int(args[1]), day=int(args[2]))
        else:
            today = datetime.date.today()

        print 'Using Report Date: %s' % today
        self.populateAppointments()

        month = today.month
        day = today.day
        year = today.year
        ninety_days_ago_datetime = today - datetime.timedelta(days=90)
        this_month_start = datetime.date(year=today.year, month=today.month, day=1)

        last_month = (today - datetime.timedelta(days=(today.day+1)))
        last_month_start = datetime.date(year=last_month.year, month=last_month.month, day=1)
        last_month_end = datetime.date(year=last_month.year, month=last_month.month, day=calendar.mdays[last_month.month])

        def messages_in_todate():
            """
            Queryset of all messages received to date.
            """
            return Message.objects.filter(direction='I')

        def messages_in_thismonth():
            return Message.objects.filter(direction='I', date__month=month)

        def messages_out_todate():
            return Message.objects.filter(direction='O')

        def messages_out_thismonth():
            return Message.objects.filter(direction='O', date__month=month)

        def get_confirmed_appts_for_month(rep_date):
            if not rep_date:
               rep_date=today
            return PatientAppointment.objects.filter(appt_date__year=rep_date.year,
                appt_date__month=rep_date.month,
                confirmed=True)

        def get_confirmed_appts_total():
            return PatientAppointment.objects.filter(confirmed=True)

        def get_all_appointments(rep_date):
            """
            Returns all the appointments made within the month of the report date
            """
            if not rep_date:
                rep_date = today
            return PatientAppointment.objects.filter(appt_date__year=rep_date.year,
                            appt_date__month=rep_date.month)

        def get_all_appointments_total():
            """
            Returns all the appointments, ever.
            """
            return PatientAppointment.objects.all()

        def total_users():
            """
            Returns a QuerySet of Contacts representing the absolute total number of users on the system.
            """
            return Contact.objects.all()

        def total_patients():
            """
            Returns a QuerySet of Contacts representing the absolute number of patients
            """
            return Contact.objects.filter(patient__isnull=False).distinct()

        def total_internal_staff():
            """
            Returns a QuerySet of Contacts representing the absolute number of study staff
            """
            return Contact.objects.filter(patient__isnull=True).distinct()

        def total_users_active():
            """
            a QuerySet of Contacts representing the total users who have been active (:= incoming messages in the last 90 days associated with this contact)
            """
            return total_users().filter(message__date__range=(ninety_days_ago_datetime,today)).distinct()

        def total_patients_active():
            """
            A QuerySet of Contacts representing the total patients who have been active (:= incoming messages in the last 90 days associated with this contact)
            """
            return total_patients().filter(message__date__range=(ninety_days_ago_datetime,today)).distinct()

        def total_staff_active():
            """
            a QuerySet of Contacts representing the total staff who have been active (:= incoming messages in the last 90 days associated with this contact)
            """
            return total_users().filter(message__date__range=(ninety_days_ago_datetime,today)).distinct()

        def get_total_confirmations(rep_date=None):
            """
            Returns a QS of the SentNotifications that are confirmed.
            If rep_date is None, will return ALL SN's in the system that have been confirmed.
            """
            sn = SentNotification.objects.filter(status__in=['confirmed','manual'])
            if rep_date:
                sn = sn.filter(date_sent__month=rep_date.month,date_sent__year=rep_date.year)
            return sn

        def get_total_sent_notifications(rep_date=None):
            """
            Gets all SentNotifications in the month of the report date argument
            If no argument is given, returns ALL SentNotifications.
            """
            sn = SentNotification.objects.all()
            if rep_date:
                sn = sn.filter(date_sent__month=rep_date.month,date_sent__year=rep_date.year)
            return sn

        def active_users():
            """
            Gets the queryset of contacts that have been active (sent a message TO the system in the last 90 days)
            """
            active_start = ninety_days_ago_datetime
            active_end = today
            active_contacts = total_users().filter(message__date__range=(active_start,active_end)).distinct()
            return active_contacts

        def active_patients():
            """
            Gets the queryset of patients that have been active (sent a message TO the system in the last 90 days)
            """
            active_start = ninety_days_ago_datetime
            active_end = today
            active_contacts = total_patients().filter(message__date__range=(active_start,active_end)).distinct()
            return active_contacts

        def active_staff():
            """
            Gets the queryset of patients that have been active (sent a message TO the system in the last 90 days)
            """
            active_start = ninety_days_ago_datetime
            active_end = today
            active_contacts = total_internal_staff().filter(message__date__range=(active_start,active_end)).distinct()
            return active_contacts

        def percentage_appts_confirmed(rep_date=None):
            if not rep_date:
                numerator = get_confirmed_appts_total().count()
                denominator = get_all_appointments_total().count()
            else:
                numerator = get_confirmed_appts_for_month(rep_date).count()
                denominator = get_all_appointments(rep_date).count()
            if denominator == 0:
                return 0
            else:
                return (numerator/(denominator*1.0))*100


        def percentage_reminders_confirmed(rep_date=None):
            numerator = get_total_confirmations(rep_date).count()
            denominator = get_total_sent_notifications(rep_date).count()
            if denominator == 0:
                return 0
            else:
                return (numerator/(denominator*1.0))*100

        pp = pprint.PrettyPrinter(indent=4).pprint
        reportValues = odict({})
        messagesValues = odict({})
        messagesValues["Messages - Incoming - To Date"] =  messages_in_todate().distinct().count()
        messagesValues["Messages - Incoming - This Month"] =   messages_in_thismonth().distinct().count()
        messagesValues["Messages - Outgoing - To Date"] =  messages_out_todate().distinct().count()
        messagesValues["Messages - Outgoing - This Month"] =  messages_out_thismonth().distinct().count()
        messagesValues["Messages - Outgoing - Patients - This Month"] =  messages_out_thismonth().filter(contact__in=total_patients()).distinct().count()
        messagesValues["Messages - Outgoing - Staff - This Month"] =  messages_out_thismonth().filter(contact__in=total_internal_staff()).distinct().count()
        messagesValues["Messages - Incoming - Patients - This Month"] =  messages_in_thismonth().filter(contact__in=total_patients()).distinct().count()
        messagesValues["Messages - Incoming - Staff - This Month"] =  messages_in_thismonth().filter(contact__in=total_internal_staff()).distinct().count()
        reportValues["Messages"] = messagesValues

        usageValues = odict({})
        usageValues["Total Users - Total"] =  total_users().count()
        usageValues["Total Users - Patients"] =  total_patients().count()
        usageValues["Total Users - Study Staff"] =  total_internal_staff().count()
        usageValues["Percentage Appointments Confirmed - To Date"] =  percentage_appts_confirmed()
        usageValues["Percentage Appointments Confirmed - This Month"] =  percentage_appts_confirmed(today)
        usageValues["Percentage Reminders Confirmed - To Date"] =  percentage_reminders_confirmed()
        usageValues["Percentage Reminders Confirmed - This Month"] =  percentage_reminders_confirmed(last_month)
        usageValues["Active Users - Number - Total"] =  active_users().count()
        usageValues["Active Users - Number - Patients"] =  active_patients().count()
        usageValues["Active Users - Number - Internal Staff"] =  active_staff().count()
        usageValues["Active Users - Percentage - Total"] =  (active_users().count()/(total_users().count()*1.0))*100
        usageValues["Active Users - Percentage - Patients"] =  (active_patients().count()/(total_patients().count()*1.0))*100
        usageValues["Active Users - Percentage - Staff"] =  (active_staff().count()/(total_internal_staff().count()*1.0))*100
        usageValues["Messages Outgoing - Avg Per User - Total"] =  (messages_out_thismonth().count()/(total_users().count()*1.0))
        usageValues["Messages Outgoing - Avg Per User - Patients"] = messages_out_thismonth().filter(contact__in=total_patients()).count()/(total_patients().count()*1.0)
        usageValues["Messages Outgoing - Avg Per User - Staff"] =  messages_out_thismonth().filter(contact__in=total_internal_staff()).count()/(total_internal_staff().count()*1.0)
        usageValues["Messages Incoming - Avg Per User - Total"] =  messages_in_thismonth().count()/(total_users().count()*1.0)
        usageValues["Messages Incoming - Avg Per User - Patients"] = messages_in_thismonth().filter(contact__in=total_patients()).count()/(total_patients().count()*1.0)
        usageValues["Messages Incoming - Avg Per User - Staff"] =  messages_in_thismonth().filter(contact__in=total_internal_staff()).count()/(total_internal_staff().count()*1.0)

        apptReminders = odict({})
        apptReminders["Total Reminders Sent - Last Month"] =  get_total_sent_notifications(last_month).count()
        apptReminders["Total Reminders Sent - This Month"] =  get_total_sent_notifications(today).count()
        apptReminders["Percentage Appts Confirmed - Last Month"] =  percentage_appts_confirmed(last_month)
        apptReminders["Percentage Appts Confirmed - This Month"] =  percentage_appts_confirmed(today)
        apptReminders["Percentage Reminders Confirmed - Last Month"] =  percentage_reminders_confirmed(last_month)
        apptReminders["Percentage Reminders Confirmed - This Month"] =  percentage_reminders_confirmed(last_month)
        apptReminders["Avg Number Reminders Per Appt - Last Month"] =  get_all_appointments(last_month).aggregate(Avg('avg_num_notifications'))["avg_num_notifications__avg"]
        apptReminders["Avg Number Reminders Per Appt - This Month"] =  get_all_appointments(today).aggregate(Avg('avg_num_notifications'))["avg_num_notifications__avg"]
        apptReminders["Avg Number of Confirmations per Appointment - Last Month"] =  get_all_appointments(last_month).aggregate(Avg('num_confirmations'))["num_confirmations__avg"]
        apptReminders["Avg Number of Confirmations per Appointment - This Month"] =  get_all_appointments(today).aggregate(Avg('num_confirmations'))["num_confirmations__avg"]

        def getBroadcastMessages(rep_date=None,recipient=None):
            bm = BroadcastMessage.objects.filter(status='sent')
            if recipient == 'patient':
                bm = bm.filter(recipient__in=total_patients())
            elif recipient == 'staff':
                bm = bm.filter(recipient__in=total_internal_staff())
            else:
                #We want all the Broadcast messages for this period
                pass
            if rep_date:
                bm = bm.filter(date_sent__year=rep_date.year, date_sent__month=rep_date.month)
            bm = bm.distinct()
            return bm

        def avgBroadcastMessages(rep_date=None,recipient=None):
            bms = getBroadcastMessages(rep_date,recipient).count()*1.0
            if recipient == 'patient':
                recps = total_patients()
            elif recipient == 'staff':
                recps = total_internal_staff()
            else:
                recps = total_users()

            recps = recps.count()*1.0

            if recps == 0:
                return None
            return bms/recps

        broadcastMessages = odict({})
        broadcastMessages["Note:"] = "Month means the entire Calendar Month's worth of data unless otherwise specified."
        broadcastMessages["Total Broadcast Messages Sent - This Month"] = getBroadcastMessages(today).count()
        broadcastMessages["Total Broadcast Messages Sent - Last Month"] = getBroadcastMessages(last_month).count()
        broadcastMessages["Num Broadcast Messages Received by Patients - This Month"] = getBroadcastMessages(today,'patient').count()
        broadcastMessages["Num Broadcast Messages Received by Patients - Last Month"] = getBroadcastMessages(last_month,'patient').count()
        broadcastMessages["Avg Num Broadcast Messages Received per Patient - This Month"] =  avgBroadcastMessages(today,'patient')
        broadcastMessages["Avg Num Broadcast Messages Received per Patient - Last Month"] =  avgBroadcastMessages(last_month,'patient')
        broadcastMessages["Num Broadcast Messages Received by Staff - This Month"] = getBroadcastMessages(today,'staff').count()
        broadcastMessages["Num Broadcast Messages Received by Staff - Last Month"] = getBroadcastMessages(last_month,'staff').count()
        broadcastMessages["Avg Num Broadcast Messages Received per Staff - This Month"] = avgBroadcastMessages(today,'staff')
        broadcastMessages["Avg Num Broadcast Messages Received per Staff - Last Month"] = avgBroadcastMessages(last_month,'staff')

        def get_callback_request(start_date,end_date):
            stuff = usage_report_context(start_date,end_date)
            return stuff['rule_data'][u'Subject'][u'Callback Request'][0]

        def get_coldchain_incoming(start_date, end_date):
            stuff = usage_report_context(start_date,end_date)
            return stuff['rule_data'][u'Cold Chain'][u'Cold Chain Alert'][0]

        stuff_this_month = usage_report_context(this_month_start,today)
        stuff_last_month = usage_report_context(last_month_start,last_month_end)


        otherMessages = odict({})
        otherMessages["Callback requests - Last Month"] = get_callback_request(last_month_start,last_month_end)
        otherMessages["Callback requests - This Month"] = get_callback_request(this_month_start,today)
        otherMessages["Cold Chain Messages Received - Last Month"] = get_coldchain_incoming(last_month_start,last_month_end)
        otherMessages["Cold Chain Messages Received - This Month"] = get_coldchain_incoming(this_month_start,today)

        apptConfs8Months = []
        reminderConfs8Months = []
        actApps8Months = []
        actBroadcasts8Months = []
        actCallbacks8Months = []
        actColdChain8Months = []




        def get_n_months_ago(n):
            """
            Returns the start of the month date of n months ago
            """
            def get_month(start_month,sub):
                if sub == 0:
                    return 0, start_month
                years = 0
                while sub > 12:
                    years += 1
                    sub -= 12

                months = 0
                if sub >= start_month:
                    years += 1
                    months =  12 + (start_month - sub)
                else:
                    months = start_month - sub

                return years, months


            start_month = today.month
            start_month_day = this_month_start.day
            start_month_days = calendar.mdays[start_month]
            (years_ago,month) = get_month(start_month,n)
            return datetime.date(year=(today.year-years_ago),month=month,day=1)

        last8monthsStartEndDates = []
        for i in range(8):
            d = get_n_months_ago(i)
            d_end = datetime.date(year=d.year, month=d.month, day=calendar.mdays[d.month])
            last8monthsStartEndDates.append('%s to %s' % (str(d),str(d_end)))
            apptConfs8Months.append(percentage_appts_confirmed(d))
            reminderConfs8Months.append(percentage_reminders_confirmed(d))
            actApps8Months.append(get_all_appointments(d).count())
            actBroadcasts8Months.append(getBroadcastMessages(d).count())
            actCallbacks8Months.append(get_callback_request(d,d_end))
            actColdChain8Months.append(get_coldchain_incoming(d,d_end))

        systemUsageByActivity = odict({})
        systemUsageByActivity["This Month - Appointments"] =  get_all_appointments(today).count()
        systemUsageByActivity["This Month - Broadcast Messages"] =  getBroadcastMessages(today).count()
        systemUsageByActivity["This Month - Callback Services"] =  get_callback_request(this_month_start,today)
        systemUsageByActivity["This Month - Cold Chain"] =  get_coldchain_incoming(this_month_start,today)
        systemUsageByActivity["Last 8 Months Dates"] =  last8monthsStartEndDates
        systemUsageByActivity["Last 8 Months % Appointments Confirmed"] =  apptConfs8Months
        systemUsageByActivity["Last 8 Months % Reminders Confirmed"] =  reminderConfs8Months
        systemUsageByActivity["Last 8 Months Total Appointments"] = actApps8Months
        systemUsageByActivity["Last 8 Months Total Broadcast Messages"] = actBroadcasts8Months
        systemUsageByActivity["Last 8 Months Total Callback Services"] = actCallbacks8Months
        systemUsageByActivity["Last 8 Months Total Cold Chain"] = actColdChain8Months

        reportValues["Usage Values"] = usageValues
        reportValues["Appointment Reminders"] = apptReminders
        reportValues["Broadcast Messages"] = broadcastMessages
        reportValues["Other Messages"] = otherMessages
        reportValues["System Usage by Activity"] = systemUsageByActivity

        print '\n\nTrialConnect Report for %s, Date: %s\n\n' % (settings.DATABASES["default"]["NAME"], today)
        for key, value in reportValues.items():
            print '#################################################'
            print '### %s ###' % key
            print '#################################################'
            for k, v in value.items():
                if isinstance(v,list):
                    v = map(str, v)
                    v = '\t'.join(v)
                print '%s\t%s' % (k, v)

#        pp(reportValues)


        
    