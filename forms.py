from django import forms
from django.conf import settings
from django.core.mail import send_mail


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
            settings.SERVER_EMAIL
        )


class UpdateForm(forms.Form):
    gedcom_file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 42M.'
    )
