from django.conf.urls import patterns, url

from gedgo import views

urlpatterns = patterns('',
    url(r'^(?P<gedcom_id>\d+)/(?P<person_id>I\d+)/$', views.person, name='person'),
    url(r'^(?P<gedcom_id>\d+)/$', views.gedcom, name='gedcom'),
    url(r'^(?P<gedcom_id>\d+)/blog/$', views.blog),
	url(r'^(?P<gedcom_id>\d+)/blog/(?P<post_id>\d+)/$', views.blogpost),
	url(r'^(?P<gedcom_id>\d+)/documentaries/$', views.documentaries),
    url(r'^search/$', views.search),
    
    # Redirects
    url(r'^blog/$', views.blog_redirect),
    url(r'^documentaries/$', views.documentaries_redirect),
    url(r'^$', views.gedcom_redirect),
)
