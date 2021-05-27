from django.conf.urls import include, url
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.views import LoginView

admin.autodiscover()

urlpatterns = [
    url(r'^$', lambda r: redirect('/gedgo/')),
    url(r'^gedgo/', include('gedgo.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', LoginView.as_view(),
        {'template_name': 'auth/login.html'}),
    url(r'^login/$', LoginView.as_view(),
        {'template_name': 'auth/login.html'}),
    url(r'^robots\.txt$',
        lambda r: HttpResponse(
            "User-agent: *\nDisallow: /",
            mimetype="text/plain"))
]
