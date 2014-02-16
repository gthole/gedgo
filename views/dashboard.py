from gedgo.forms import UpdateForm
from gedgo.tasks import async_update
from gedgo.views.util import render
from gedgo.models import Gedcom
from gedgo import REDIS

from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.contrib import messages
from django.shortcuts import redirect

import datetime
import time
import json
from collections import defaultdict


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        raise Http404

    form = None
    if request.POST:
        form = UpdateForm(request.POST, request.FILES)
        _handle_upload(request, form)
        return redirect('/gedgo/dashboard/')

    if form is None:
        form = UpdateForm()

    # Collect tracking stats from Redis storage
    views, user_views, total = _page_view_stats()

    # Render list page with the documents and the form
    return render(
        request,
        'dashboard.html',
        {
            'form': form,
            'views': views,
            'user_views': user_views,
            'total': total,
            'gedcoms': Gedcom.objects.iterator()
        }
    )


def _page_view_stats():
    if REDIS is None:
        return {}
    page_views = [
        json.loads(m) for m in
        REDIS.lrange('gedgo_page_views', 0, -1)
    ]

    # Take the 20 most recent page views, format the time.
    view_sample = page_views[:20]
    for vs in view_sample:
        vs['time'] = datetime.datetime.fromtimestamp(int(vs['time']))

    # Tally the usernames across all recently recorded views.
    user_views = defaultdict(int)
    for pv in page_views:
        user_views[pv['username']] += 1

    return view_sample, user_views.items(), REDIS.get('gedgo_page_view_count')


def _handle_upload(request, form):
    if form.is_valid():
        file_name = 'uploaded/gedcoms/%d_%s' % (
            time.time(), form.cleaned_data['gedcom_file'].name)
        default_storage.save(file_name, form.cleaned_data['gedcom_file'])
        async_update.delay(form.cleaned_data['gedcom_id'], file_name)
        messages.success(
            request,
            'Your gedcom file has been uploaded and the database will '
            'be updated momentarily.'
        )
    else:
        messages.error(
            request,
            'Something went wrong with your upload, '
            'please try again later.'
        )
