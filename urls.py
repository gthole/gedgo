from django.conf.urls import patterns, url, include
from django.views.generic.simple import redirect_to
from gedgo.api import PersonResource

from gedgo import views

person_resource = PersonResource()

urlpatterns = patterns('',
	url(r'^(?P<gedcom_id>\d+)/(?P<person_id>I\d+)/$', views.person, name='person'),
	url(r'^(?P<gedcom_id>\d+)/(?P<family_id>F\d+)/$', views.family, name='family'),
	url(r'^(?P<gedcom_id>\d+)/$', views.gedcom, name='gedcom'),
	url(r'^(?P<gedcom_id>\d+)/blog/$', views.blog_list),
	url(r'^(?P<gedcom_id>\d+)/blog/(?P<year>\d+)/(?P<month>\d+)/$', views.blog),
	url(r'^(?P<gedcom_id>\d+)/blog/post/(?P<post_id>\d+)/$', views.blogpost),
	url(r'^(?P<gedcom_id>\d+)/documentaries/$', views.documentaries),
	url(r'^(?P<gedcom_id>\d+)/update/$', views.update_view),
	url(r'^api/', include(person_resource.urls)),
	url(r'^search/$', views.search),

	# Redirects
	url(r'^blog/$', redirect_to, {'url': '/gedgo/1/blog/'}),
	url(r'^documentaries/$', redirect_to, {'url': '/gedgo/1/documentaries/'}),
	url(r'^$', redirect_to, {'url': '/gedgo/1/'}),
)
