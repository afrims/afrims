from django.conf.urls.defaults import *
from afrims.apps.broadcast import views


urlpatterns = patterns('',
    url(r'^send/$', views.send_message, name='send-message'),
    url(r'^schedule/$', views.schedule, name='broadcast-schedule'),
    url(r'^messages/$', views.messages, name='broadcast-messages'),
)

