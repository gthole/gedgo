from django import forms

class CommentForm(forms.Form):
	name = forms.CharField()
	email = forms.EmailField(required=False)
	message = forms.CharField()