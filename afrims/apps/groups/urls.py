from django.conf.urls.defaults import *
from afrims.apps.groups import views


urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='groups-dashboard'),
)