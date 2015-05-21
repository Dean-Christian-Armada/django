from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from list.models import Members, Marines

# Create your views here.
@login_required
def index(request):
	template = 'guests/index.html'
	name = request.session['name']
	members = Members.objects.get(name=name)
	marines = Marines.objects.get(members=members)
	context_dict = { 'marine': marines  }
	return render(request, template, context_dict)
# @login_required
# def user_logout(request):
# 	logout(request)
# 	return HttpResponseRedirect('/')