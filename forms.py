from django import forms
from django.conf import settings
from django.core.mail import send_mail


class CommentForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(required=False)
    message = forms.CharField()

    def email_comment(self, noun):
        cd = self.cleaned_data
        send_mail(
            'Comment from %s about %s' % (cd['name'], noun),
            cd['message'],
            cd.get('email', 'noreply@gedgo.com'),
            settings.SERVER_EMAIL
        )


class UpdateForm(forms.Form):
    gedcom_file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 42M.'
    )
