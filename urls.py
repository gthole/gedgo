from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from gedgo import views

urlpatterns = patterns('',
    url(r'^(?P<person_id>I\d+)/$', views.person, name='person'),
    url(r'^search/$', views.search),
)

urlpatterns += staticfiles_urlpatterns()