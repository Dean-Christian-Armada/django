from django import forms
from .models import Members

class MembersForm(forms.ModelForm):
	class Meta:
		model = Members
		fields = ('title', 'name', 'country', 'gender', 'city')