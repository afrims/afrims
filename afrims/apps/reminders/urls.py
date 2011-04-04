from django.conf.urls.defaults import *

from afrims.apps.reminders import views

urlpatterns = patterns('',
    url(r'^create/$', views.create_edit_notification, name='create-notification'),
    url(r'^(\d+)/edit/$', views.create_edit_notification, name='edit-notification'),
    url(r'^(\d+)/delete/$', views.delete_notification, name='delete-notification'),
    url(r'^$', views.dashboard, name='reminders_dashboard'),
    url(r'report/$', views.report, name='reminders-report'),
    url(r'post$', views.receive_patient_record, name='patient-import'),
)
