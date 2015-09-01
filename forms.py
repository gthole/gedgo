from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from gedgo.models import Gedcom


class CommentForm(forms.Form):
    message = forms.CharField()

    def email_comment(self, user, noun, file_names):
        cd = self.cleaned_data
        message_body = '%s\n\n%s' % (cd['message'], '\n'.join(file_names))
        send_mail(
            'Comment from %s %s about %s' % (
                user.first_name,
                user.last_name,
                noun
            ),
            message_body,
            'noreply@gedgo.com',
            settings.SERVER_EMAIL
        )


class UpdateForm(forms.Form):
    gedcom_id = forms.IntegerField()
    gedcom_file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 42M.'
    )
    email_users = forms.TypedMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[(a, str(a)) for a in range(100)]  # TODO: Unhack
    )
    message = forms.CharField(required=False)

    def is_valid(self):
        if not super(UpdateForm, self).is_valid():
            self.error_message = 'Please upload a valid gedcom file.'
            return False
        data = self.cleaned_data
        self.gedcom = get_object_or_404(Gedcom, id=data['gedcom_id'])
        for id_ in data['email_users']:
            get_object_or_404(User, pk=id_)
        if data['email_users'] and not data['message']:
            self.error_message = 'You must enter a message if emailing users.'
            return False

        return True
