from django.conf.urls.defaults import *

from afrims.apps.reminders import views

urlpatterns = patterns('',
    url(r'^create/$', views.create_edit_notification, name='create-notification'),
    url(r'^edit/(\d+)/$', views.create_edit_notification, name='edit-notification'),
    url(r'^$', views.dashboard, name='reminders_dashboard'),
    url(r'post$', views.receive_patient_record, name='patient-import')
)
