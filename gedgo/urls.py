from django.conf.urls import url
from django.shortcuts import redirect
from django.contrib.auth.views import password_reset, password_reset_done, \
    password_reset_confirm

from gedgo import views

urlpatterns = [
    url(
        r'^(?P<gedcom_id>\d+)/(?P<person_id>I\d+)/$',
        views.person,
        name='person'
    ),
    url(r'^(?P<gedcom_id>\d+)/$', views.gedcom, name='gedcom'),

    # XHR Data views
    url(r'^(?P<gid>\d+)/pedigree/(?P<pid>I\d+)/$', views.pedigree),
    url(r'^(?P<gid>\d+)/timeline/(?P<pid>I\d+)/$', views.timeline),
    url(r'^dashboard/worker/status$', views.worker_status),

    url(r'^blog/$', views.blog_list),
    url(r'^blog/(?P<year>\d+)/(?P<month>\d+)/$', views.blog),
    url(r'^blog/post/(?P<post_id>\d+)/$', views.blogpost),
    url(r'^documentaries/$', views.documentaries),
    url(r'^research/(?P<pathname>.*)$', views.research),
    url(r'^search/$', views.search),
    url(r'^dashboard/$', views.dashboard),
    url(r'^dashboard/user/(?P<user_id>\d+)/$', views.user_tracking),

    # Auth
    url(r'^logout/$', views.logout_view),
    url(r'^password_reset/$',
        password_reset,
        {
            'template_name': 'auth/login.html',
            'email_template_name': 'auth/password_reset_email.html',
            'post_reset_redirect': '/gedgo/password_reset/done/'
        }),
    url(r'^password_reset/done/$',
        password_reset_done,
        {
            'template_name': 'auth/password_reset_done.html'
        }),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        {
            'post_reset_redirect': '/',
            'template_name': 'auth/password_reset_confirm.html'
        }),

    # Backup media fileserve view
    url(r'^media/(?P<file_base_name>.*)$', views.media),

    url(r'^$', lambda r: redirect('/gedgo/1/')),
]
