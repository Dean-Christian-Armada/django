from django import template
from list.models import Members
from django.http import HttpResponse
from list.forms import MembersForm

register = template.Library()

@register.inclusion_tag('list/add_member.html', takes_context=True)
def sample(context):
	request = context['request']
	form = MembersForm()
	boolean = 'false'
	if request.method == 'POST' and 'submit' in request.POST:
		form = MembersForm(request.POST)
		if form.is_valid():
			title = request.POST.get('title')
			name = request.POST.get('name')
			country = request.POST.get('country')
			gender = request.POST.get('gender')
			city = request.POST.get('city')
			new_member = Members.objects.get_or_create(title = title, name = name, country = country, gender = gender, city = city)
		else:
			print form.errors
			boolean = 'true'
	context_dict = { 'form': form, 'boolean': boolean, 'button': 'submit' }
	return context_dict
# def updates(context):
# 	title = 'titles'
# 	name = 'names'
# 	country = 'countries'
# 	gender = 'genders'
# 	email = 'emails'
# 	parameters = {'title': title, 'name': name, 'country': country, 'gender': gender, 'email': email }
# 	form = MembersForm(initial = parameters)
# 	context_dict = { 'form': form }
# 	return context_dict