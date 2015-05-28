from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from .models import Members, Marines
from .forms import MembersForm, MembersUpdate, MarinesForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.template import RequestContext

# Create your views here.
@login_required
def index(request):
	template = 'list/index.html'
	members = Members.objects.all().filter(IsActive=True, userlevel='2')
	context_dict = {'members': members}
	return render(request, template, context_dict)
@login_required	
def manual(request):
	template = 'list/manual.html'
	context_dict = {}
	return render(request, template, context_dict)
@login_required	
def delete_member(request):
	if request.method == 'GET':
	 	id = request.GET.get('id');
	 	# return HttpResponse(id);
		members = Members.objects.get(pk=id)
		members.delete()
	template = 'list/trash_members.html'
	members = Members.objects.all().filter(IsActive=False, userlevel='2')
	context_dict = {'members': members}
	return render(request, template, context_dict)
@login_required	
def update_form(request):
	if request.method == 'POST':
		code = request.POST.get('code')
		if code:
			code = request.POST.get('code')
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
				print "dean"
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
			members = Members.objects.get(code=code)
			members.title = title
			members.name = name
			members.country = country
			members.gender = gender
			members.city = city
			members.save()
			marines = Marines.objects.get(members=members)
			marines.cert_name = cert_name
			marines.cert_number = cert_number
			if picture:
				marines.picture = picture
			marines.date_issue = date_issue
			marines.date_expire = date_expire
			marines.save()
			template = 'list/members.html'
			# members = Members.objects.all().filter(IsActive=True, userlevel='2')
			# context_dict = {'members': members}
			# return render(request, template, context_dict)
			return HttpResponseRedirect('/staff/')
	else:
		update_id = request.GET.get('update_id')
		if update_id:
			members = Members.objects.get(pk=update_id)
			code = members.code
			title = members.title
			name = members.name
			country = members.country
			gender = members.gender
			city = members.city
			marines = Marines.objects.get(members=members)
			cert_name = marines.cert_name
			cert_number = marines.cert_number
			picture = marines.picture
			date_issue = marines.date_issue
			date_expire = marines.date_expire
			initial = {'code': code,'title': title, 'name': name, 'country': country, 'gender': gender, 'city': city }
			marine_initial = {'cert_name': cert_name, 'cert_number': cert_number, 'picture': picture, 'date_issue': date_issue, 'date_expire': date_expire}
			update_form = MembersUpdate(initial = initial)
			update_marine_form = MarinesForm(initial = marine_initial)
			context_dict = { 'update_form': update_form, 'update_marine_form': update_marine_form, 'button': 'update', 'id': update_id }
			template = 'list/update_member.html'
			return render(request, template, context_dict)
@login_required
def search_names(request):
	name = '';
	if request.method == 'GET':
		name = request.GET.get('name')
		if name:
			name = Members.objects.filter(name__istartswith=name)
		else:
			name = Members.objects.all()	
	template = 'list/members.html'
	context_dict = { 'members': name }
	return render(request, template, context_dict)
@login_required
def view_cert(request):
	id = ''
	template = 'list/view_cert.html'
	if request.method == 'GET':
		if 'id' in request.GET:
			id = request.GET.get('id')
			if 'info' in request.GET:
				template = 'list/view_cert_info.html'
	members = Members.objects.get(pk=id)
	marines = Marines.objects.get(members=members)	
	context_dict = { 'marines': marines, 'members': members }
	# return render(request, template, context_dict)
	return render_to_response(template, context_dict, context_instance=RequestContext(request))
@login_required
def trash(request):
	if request.method == 'GET':
	 	id = request.GET.get('id');
		members = Members.objects.get(pk=id)
		members.IsActive = False
		members.save()
	template = 'list/members.html'
	members = Members.objects.all().filter(IsActive=True, userlevel='2')
	context_dict = {'members': members}
	return render(request, template, context_dict)
@login_required
def recycle_bin(request):
	template = 'list/trash.html'
	members = Members.objects.all().filter(IsActive=False, userlevel='2')
	context_dict = {'members': members}
	return render(request, template, context_dict)

@login_required
def restore_member(request):
	if request.method == 'GET':
	 	id = request.GET.get('id');
		members = Members.objects.get(pk=id)
		members.IsActive = True
		members.save()
	template = 'list/trash_members.html'
	members = Members.objects.all().filter(IsActive=False, userlevel='2')
	context_dict = {'members': members}
	return render(request, template, context_dict)