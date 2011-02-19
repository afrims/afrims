from django.conf.urls.defaults import *

from afrims.apps.groups import views


urlpatterns = patterns('',
    url(r'^group/$', views.list_groups,
        name='list-groups'),
    url(r'^group/create/$', views.create_edit_group,
        name='create-group'),
    url(r'^group/(\d+)/$', views.create_edit_group,
        name='edit-group'),
    url(r'^group/(\d+)/delete/$', views.delete_group,
        name='delete-group'),
)

