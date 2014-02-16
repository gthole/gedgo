from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from gedgo.models import Gedcom


class CommentForm(forms.Form):
    message = forms.CharField()

    def email_comment(self, user, noun, file_names):
        cd = self.cleaned_data
        message_body = '%s\n\n%s' % (cd['message'], '\n'.join(file_names))
        send_mail(
            'Comment from %s %s about %s' % (
                user.first_name, user.last_name, noun),
            message_body,
            user.email or 'noreply@gedgo.com',
            [email for _, email in settings.ADMINS]
        )


class UpdateForm(forms.Form):
    gedcom_id = forms.IntegerField()
    gedcom_file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 42M.'
    )

    def is_valid(self):
        if not super(UpdateForm, self).is_valid():
            return False
        self.gedcom = get_object_or_404(
            Gedcom,
            id=self.cleaned_data['gedcom_id']
        )
        return True
