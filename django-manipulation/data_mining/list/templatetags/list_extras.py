from django import template
from list.models import Members, Userlevel, Marines
from django.http import HttpResponse, HttpResponseRedirect
from list.forms import MembersForm, MarinesForm
import hashlib

register = template.Library()

@register.inclusion_tag('list/add_member.html', takes_context=True)
def sample(context):
	request = context['request']
	form = MembersForm()
	marines_form = MarinesForm()
	boolean = 'false'
	if request.method == 'POST' and 'submit' in request.POST:
		form = MembersForm(request.POST)
		marines_form = MarinesForm(request.POST)
		if form.is_valid() and marines_form.is_valid():
			userlevel = Userlevel.objects.get(userlevel = 'seamen')
			username = request.POST.get('username')
			password = request.POST.get('password')
			# password = hashlib.md5(password).hexdigest()
			title = request.POST.get('title')
			name = request.POST.get('name')
			name = name.title()
			country = request.POST.get('country')
			gender = request.POST.get('gender')
			city = request.POST.get('city')
			city = city.title()
			cert_name = request.POST.get('cert_name')
			cert_number = request.POST.get('cert_number')
			if 'picture' in request.FILES:
				picture = request.FILES['picture']
			else:
				picture = ''
			# picture = request.POST.get('picture')
			date_issue_year = request.POST.get('date_issue_year')
			date_issue_month = request.POST.get('date_issue_month')
			date_issue_day = request.POST.get('date_issue_day')
			date_issue = date_issue_year+'-'+date_issue_month+'-'+date_issue_day
			date_expire_year = request.POST.get('date_expire_year')
			date_expire_month = request.POST.get('date_expire_month')
			date_expire_day = request.POST.get('date_expire_day')
			date_expire = date_expire_year+'-'+date_expire_month+'-'+date_expire_day
			me = Members.objects.get_or_create(userlevel=userlevel, name=name, password=password)[0]
			me.title = title
			me.name = name
			me.username = username
			me.country = country
			me.gender = gender
			me.city = city
			me.save()			
			ma = Marines.objects.get_or_create(members=me)[0]
			ma.cert_name = cert_name
			ma.cert_number = cert_number
			ma.picture = picture
			ma.date_issue = date_issue
			ma.date_expire = date_expire
			ma.save()
			# return HttpResponseRedirect('/staff/')
		else:
			print form.errors, marines_form.errors
			boolean = 'true'
	context_dict = { 'form': form, 'marines_form': marines_form, 'boolean': boolean, 'button': 'submit' }
	return context_dict