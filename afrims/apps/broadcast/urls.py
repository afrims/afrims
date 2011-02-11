from django.conf.urls.defaults import *
from afrims.apps.broadcast import views


urlpatterns = patterns('',
    url(r'^send/$', views.send_message, name='send-message'),
    url(r'^sent/$', views.message_sent),
)

