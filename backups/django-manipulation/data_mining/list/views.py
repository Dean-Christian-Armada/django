from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Members
from .forms import MembersForm, MembersUpdate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
@login_required
def index(request):
	template = 'list/index.html'
	members = Members.objects.all().filter(IsActive=True)
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
	template = 'list/members.html'
	members = Members.objects.all()	
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
			country = request.POST.get('country')
			gender = request.POST.get('gender')
			city = request.POST.get('city')
			members = Members.objects.get(code=code)
			members.title = title
			members.name = name
			members.country = country
			members.gender = gender
			members.city = city
			members.save()
			template = 'list/members.html'
			# members = Members.objects.all().filter(IsActive=True)
			# context_dict = {'members': members}
			# return render(request, template, context_dict)
			return HttpResponseRedirect('/list/')
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
			initial = {'code': code,'title': title, 'name': name, 'country': country, 'gender': gender, 'city': city }	
			update_form = MembersUpdate(initial = initial)
			context_dict = { 'update_form': update_form, 'button': 'update', 'id': update_id }
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
def user_logout(request):
	logout(request)
	return redirect('/')
