from django.conf.urls import patterns, url
from django.conf.urls import include
from django.shortcuts import redirect
from django.contrib.auth.views import password_reset
from tastypie.api import Api
from gedgo.api import PersonResource, FamilyResource

from gedgo import views

v1_api = Api(api_name='v1')
v1_api.register(PersonResource())
v1_api.register(FamilyResource())

urlpatterns = patterns(
    '',
    url(
        r'^(?P<gedcom_id>\d+)/(?P<person_id>I\d+)/$',
        views.person,
        name='person'
    ),
    url(
        r'^(?P<gedcom_id>\d+)/(?P<family_id>F\d+)/$',
        views.family,
        name='family'
    ),
    url(r'^(?P<gedcom_id>\d+)/$', views.gedcom, name='gedcom'),
    url(r'^(?P<gedcom_id>\d+)/update/$', views.update_view),

    # XHR Data views
    url(r'^(?P<gid>\d+)/pedigree/(?P<pid>I\d+)/$', views.pedigree),
    url(r'^(?P<gid>\d+)/timeline/(?P<pid>I\d+)/$', views.timeline),

    url(r'^blog/$', views.blog_list),
    url(r'^blog/(?P<year>\d+)/(?P<month>\d+)/$', views.blog),
    url(r'^blog/post/(?P<post_id>\d+)/$', views.blogpost),
    url(r'^documentaries/$', views.documentaries),
    url(r'^researchfiles/(?P<pathname>.*)$', views.researchfiles),
    url(r'^api/', include(v1_api.urls)),
    url(r'^search/$', views.search),
    url(r'^logout/$', views.logout_view),
    url(r'^/accounts/password/reset/$', password_reset,
        {'template_name': 'gedgo/password_reset.html'}),

    # Backup media fileserve view
    url(r'^media/(?P<file_base_name>.*)$', views.media),

    url(r'^$', lambda r: redirect('/gedgo/1/')),
)
