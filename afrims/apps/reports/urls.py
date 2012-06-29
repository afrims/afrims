from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'afrims.apps.reports.views.dashboard', name='rapidsms-dashboard'),
    url(r'^graphs/system-usage/$', 'afrims.apps.reports.views.system_usage', name='report-system-usage'),
    url(r'^graphs/reminder-usage/$', 'afrims.apps.reports.views.reminder_usage', name='report-reminder-usage'),
)
