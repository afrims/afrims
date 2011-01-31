'''
Created on Jan 6, 2011

@author: adewinter
'''
from django.conf.urls.defaults import *
from apps.broadcast import views

urlpatterns = patterns('',
    url(r'^contacts_table/$',views.contacts_table),
    url(r'^groups_table/$',views.groups_table),
    url(r'^$', views.dashboard),
)