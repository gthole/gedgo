from gedgo.forms import UpdateForm
from gedgo.tasks import app, async_update
from gedgo.views.util import render
from gedgo.models import Gedcom
from gedgo import REDIS

from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.shortcuts import get_object_or_404

import datetime
import time
import json
import os


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        raise Http404

    form = None
    if request.POST and request.GET.get('reset_tracking'):
        _reset_tracking()
        return redirect('/gedgo/dashboard/')
    elif request.POST:
        form = UpdateForm(request.POST, request.FILES)
        _handle_upload(request, form)
        return redirect('/gedgo/dashboard/')

    if form is None:
        form = UpdateForm()

    # Collect tracking stats from Redis storage
    tracking_start, user_views, total = _page_view_stats()

    # Render list page with the documents and the form
    return render(
        request,
        'dashboard.html',
        {
            'form': form,
            'tracking_start': tracking_start,
            'users': User.objects.filter(email__contains='@').iterator(),
            'user_views': user_views,
            'total': total,
            'gedcoms': Gedcom.objects.iterator()
        }
    )


@login_required
def worker_status(request):
    """
    XHR view for whether the celery worker is up
    """
    try:
        status = app.control.ping() or []
    except:
        # TODO: What celery exceptions are we catching here?
        status = []
    return HttpResponse(
        json.dumps(status),
        content_type="application/json"
    )


@login_required
def user_tracking(request, user_id):
    if not request.user.is_superuser:
        raise Http404

    user = get_object_or_404(User, id=user_id)
    count = REDIS.keys('gedgo_user_%d_page_view_count' % user.id)
    if not count:
        raise Http404

    views = REDIS.lrange('gedgo_user_%d_page_views' % user.id, 0, -1)
    views = [_load_page_view(v) for v in views]

    return render(
        request,
        'user_tracking.html',
        {
            'user': user,
            'count': count,
            'views': views
        }
    )


def _handle_upload(request, form):
    if form.is_valid():
        file_name = 'uploaded/gedcoms/%d_%s' % (
            time.time(), form.cleaned_data['gedcom_file'].name)
        default_storage.save(file_name, form.cleaned_data['gedcom_file'])
        async_update.delay(
            form.cleaned_data['gedcom_id'],
            os.path.join(settings.MEDIA_ROOT, file_name),
            form.cleaned_data['email_users'],
            form.cleaned_data['message'],
            get_current_site(request).domain,
            request.user.id
        )
        messages.success(
            request,
            'Your gedcom file has been uploaded and the database will '
            'be updated momentarily.'
        )
    else:
        error_message = ('Something went wrong with your upload, '
                         'please try again later.')
        if hasattr(form, 'error_message'):
            error_message = form.error_message
        messages.error(request, error_message)


def _reset_tracking():
    if REDIS is None:
        return {}

    keys = REDIS.keys('gedgo_*')
    for key in keys:
        REDIS.delete(key)

    REDIS.set('gedgo_tracking_start', int(time.time()))


def _page_view_stats():
    if REDIS is None:
        return {}

    user_keys = REDIS.keys('gedgo_user_*_page_view_count')
    users = User.objects.filter(
        id__in=[int(k.split('_')[2]) for k in user_keys]
    )

    user_views = []
    for user in users:
        last = REDIS.lrange('gedgo_user_%d_page_views' % user.id, 0, 0)[0]
        pvc = REDIS.get('gedgo_user_%d_page_view_count' % user.id)
        user_views.append({
            'user': user,
            'last_view': _load_page_view(last)['timestamp'],
            'count': pvc
        })
    user_views = sorted(user_views, key=lambda x: x['last_view'], reverse=True)

    tracking_start = _timestamp_from_redis('gedgo_tracking_start')

    return tracking_start, user_views, REDIS.get('gedgo_page_view_count')


def _load_page_view(json_str):
    view = json.loads(json_str)
    view['timestamp'] = datetime.datetime.fromtimestamp(int(view['time']))
    return view


def _timestamp_from_redis(key):
    try:
        timestamp = REDIS.get(key)
        return datetime.datetime.fromtimestamp(int(timestamp))
    except:
        pass
