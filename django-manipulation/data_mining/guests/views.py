from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
@login_required
def index(request):
	template = 'guests/index.html'
	# members = Members.objects.all().filter(IsActive=True)
	context_dict = { }
	return render(request, template, context_dict)
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')