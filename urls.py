from django.conf.urls import include, url
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.views import login

admin.autodiscover()

urlpatterns = [
    url(r'^$', lambda r: redirect('/gedgo/')),
    url(r'^gedgo/', include('gedgo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login,
        {'template_name': 'auth/login.html'}),
    url(r'^login/$', login,
        {'template_name': 'auth/login.html'}),
    url(r'^robots\.txt$',
        lambda r: HttpResponse(
            "User-agent: *\nDisallow: /",
            mimetype="text/plain"))
]
