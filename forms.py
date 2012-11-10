from django import forms
from django.conf import settings
from django.core.mail import send_mail

class CommentForm(forms.Form):
	name = forms.CharField()
	email = forms.EmailField(required=False)
	message = forms.CharField()

def comment_action(request, noun):
	form = CommentForm(request.POST)
	if form.is_valid():
		cd = form.cleaned_data
		send_mail(
			'Comment from ' + cd['name'] + ' about ' + noun,
			cd['message'],
			cd.get('email', 'noreply@example.com'),
			[settings.SERVER_EMAIL],
		)
		return form

class UpdateForm(forms.Form):
    gedcom_file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 42M.'
    )
