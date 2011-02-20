from django.conf.urls.defaults import *
from afrims.apps.broadcast import views


urlpatterns = patterns('',
    url(r'^send/$', views.send_message, name='send-message'),
    url(r'^schedule/$', views.schedule, name='broadcast-schedule'),
    url(r'^schedule/(?P<broadcast_id>\d+)/edit/$', views.send_message,
        name='edit-broadcast'),
    url(r'^schedule/(?P<broadcast_id>\d+)/delete/$', views.delete_broadcast,
        name='delete-broadcast'),
    url(r'^messages/$', views.list_messages, name='broadcast-messages'),
)

