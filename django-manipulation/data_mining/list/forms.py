from django import forms
from .models import Members

class MembersForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = Members
		fields = ('username','password','title', 'name', 'country', 'gender', 'city',)

class MembersUpdate(forms.ModelForm):
	code = forms.CharField(widget = forms.HiddenInput())
	name = forms.CharField()
	class Meta:
		model = Members
		fields = ('code', 'title', 'name', 'country', 'gender', 'city',)