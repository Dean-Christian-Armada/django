from django import forms
from .models import Members

class MembersForm(forms.ModelForm):
	class Meta:
		model = Members
		fields = ('title', 'name', 'country', 'gender', 'city',)

class MembersUpdate(forms.ModelForm):
	code = forms.CharField(widget = forms.HiddenInput())
	name = forms.CharField()
	class Meta:
		model = Members
		fields = ('code', 'title', 'name', 'country', 'gender', 'city',)