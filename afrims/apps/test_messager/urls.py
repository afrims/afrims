from django.conf.urls.defaults import *
from afrims.apps.test_messager import views


urlpatterns = patterns('',
    url(r'^form/$', views.message_form, name='send-test-message-form'),
)

