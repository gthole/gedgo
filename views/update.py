from gedgo.models import Gedcom
from gedgo.forms import UpdateForm
from gedgo.tasks import async_update
from gedgo.views.util import render

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from celery.task.control import inspect


@login_required
def update_view(request, gedcom_id):
    if not request.user.is_superuser:
        return redirect('/gedgo')

    g = get_object_or_404(Gedcom, id=gedcom_id)
    message = ''
    celerystate = inspect()

    if celerystate.active() is not None:  # TODO: Check task names.
        form = ''
        message = ('This gedcom is currently being updated already.'
                   'Please check back later.')
    elif request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES)
        # check for temp file
        if form.is_valid():
            # TODO: Make friendly to other OSes.
            content = request.FILES['gedcom_file'].read().split("\r")

            # Call celery worker
            async_update.delay(g, content)

            # Redirect to the document list after POST
            form = ''
            message = 'Upload successful. Gedcom updating.'
        else:
            form = UpdateForm()
            message = 'Did you correctly upload a gedcom file?'

    else:
        form = UpdateForm()

    # Render list page with the documents and the form
    return render(
        request,
        'gedgo/update.html',
        {'form': form, 'message': message, 'gedcom': g},
    )
