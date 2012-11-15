from django.conf.urls import patterns, url

from gedgo import views

urlpatterns = patterns('',
    url(r'^(?P<gedcom_id>\d+)/(?P<person_id>I\d+)/$', views.person, name='person'),
    url(r'^(?P<gedcom_id>\d+)/(?P<family_id>F\d+)/$', views.family, name='family'),
    url(r'^(?P<gedcom_id>\d+)/$', views.gedcom, name='gedcom'),
    url(r'^(?P<gedcom_id>\d+)/blog/$', views.blog_list),
    url(r'^(?P<gedcom_id>\d+)/blog/(?P<year>\d+)/(?P<month>\d+)/$', views.blog),
	url(r'^(?P<gedcom_id>\d+)/blog/post/(?P<post_id>\d+)/$', views.blogpost),
	url(r'^(?P<gedcom_id>\d+)/documentaries/$', views.documentaries),
	url(r'^(?P<gedcom_id>\d+)/update/$', views.update),
    url(r'^search/$', views.search),
    
    # Redirects
    url(r'^blog/$', views.blog_redirect),
    url(r'^documentaries/$', views.documentaries_redirect),
    url(r'^$', views.gedcom_redirect),
)
