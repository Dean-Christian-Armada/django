from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from list.models import Members
import hashlib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
	context_dict = {}
	template = 'index.html'
	# return HttpResponse('Homepage'
	return render(request, template, context_dict)
def validation(request):
	username = ''
	password = ''
	if request.method == 'POST':
		if 'username' in request.POST and 'password' in request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username=username, password=password)
			if user:
				login(request, user)
				redirect = "/admin/"
			else:
				password = hashlib.md5(password).hexdigest()
				try:
					me = Members.objects.get(username=username, password=password)
					userlevel = me.userlevel
					name = me.name
					userlevel = str(userlevel)
					if userlevel == 'seamen':
						username = "seamen"
						password = "seamen"
						redirect = '/seamen/'
					elif userlevel == 'staff':
						username = "staff"
						password = "staff"
						redirect = '/staff/'
					else:
						username = "admin"
						password = "d3@narmada13"
						redirect = '/admin/login/?next=/admin/'
				except Members.DoesNotExist:
					return HttpResponseRedirect('/')
				# request.session['name'] = name	
				user = authenticate(username=username, password=password)
				if user:
					if user.is_active:
						login(request, user)
	# 		else:
	# 			redirect = '/'
	# 	else:
	# 		redirect = '/'
	# else:
	# 	redirect = '/'
	return HttpResponseRedirect(redirect)
	# context_dict = {}
	# template = ''
	# return HttpResponse('Homepage')
	# return render(request, template, context_dict)
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')