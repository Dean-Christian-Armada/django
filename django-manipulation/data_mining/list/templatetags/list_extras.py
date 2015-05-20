from django import template
from list.models import Members, Userlevel
from django.http import HttpResponse, HttpResponseRedirect
from list.forms import MembersForm
import hashlib

register = template.Library()

@register.inclusion_tag('list/add_member.html', takes_context=True)
def sample(context):
	request = context['request']
	form = MembersForm()
	boolean = 'false'
	if request.method == 'POST' and 'submit' in request.POST:
		form = MembersForm(request.POST)
		if form.is_valid():
			userlevel = Userlevel.objects.get(userlevel = 'seamen')
			username = request.POST.get('username')
			password = request.POST.get('password')
			# password = hashlib.md5(password).hexdigest()
			title = request.POST.get('title')
			name = request.POST.get('name')
			country = request.POST.get('country')
			gender = request.POST.get('gender')
			city = request.POST.get('city')
			new_member = Members.objects.get_or_create(userlevel=userlevel, username=username, password=password, title = title, name = name, country = country, gender = gender, city = city)
			HttpResponseRedirect('/staff/')
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