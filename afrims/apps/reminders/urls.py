from django.conf.urls.defaults import *

from afrims.apps.reminders import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='reminders_dashboard'),
)
