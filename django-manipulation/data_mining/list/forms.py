from django import forms
from .models import Members, Marines
from django.forms.extras.widgets import SelectDateWidget

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

class MarinesForm(forms.ModelForm):
	date_issue = forms.DateField(widget=SelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day")))
	date_expire = forms.DateField(widget=SelectDateWidget(empty_label="Nothing"))
	class Meta:
		model = Marines
		fields = ('cert_name', 'cert_number', 'picture','date_issue','date_expire',)