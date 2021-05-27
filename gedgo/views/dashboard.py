from gedgo.forms import UpdateForm
from gedgo.tasks import async_update
from gedgo.views.util import render
from gedgo.models import Gedcom

from django_simple_task import defer

from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.contrib import messages
from django.shortcuts import redirect
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
    if request.POST:
        form = UpdateForm(request.POST, request.FILES)
        _handle_upload(request, form)
        return redirect('/gedgo/dashboard/')

    if form is None:
        form = UpdateForm()

    # Render list page with the documents and the form
    return render(
        request,
        'dashboard.html',
        {
            'form': form,
            'users': User.objects.filter(email__contains='@').iterator(),
            'gedcoms': Gedcom.objects.iterator()
        }
    )


@login_required
def worker_status(request):
    """
    XHR view for whether the celery worker is up
    """
    try:
        status = [True]
    except Exception:
        # TODO: What celery exceptions are we catching here?
        status = []
    return HttpResponse(
        json.dumps(status),
        content_type="application/json"
    )


def _handle_upload(request, form):
    if form.is_valid():
        file_name = 'uploads/gedcoms/%d_%s' % (
            time.time(), form.cleaned_data['gedcom_file'].name)
        default_storage.save(file_name, form.cleaned_data['gedcom_file'])
        defer(async_update, {
            'args': [
                form.cleaned_data['gedcom_id'],
                os.path.join(settings.MEDIA_ROOT, file_name),
                form.cleaned_data['email_users'],
                form.cleaned_data['message'],
                request.get_host(),
                request.user.id,
            ]
        })
        messages.success(
            request,
            'Your gedcom file has been uploaded and the database will '
            'be processed shortly.'
        )
    else:
        error_message = ('Something went wrong with your upload, '
                         'please try again later.')
        if hasattr(form, 'error_message'):
            error_message = form.error_message
        messages.error(request, error_message)
