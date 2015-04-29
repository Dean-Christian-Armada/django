from django.shortcuts import render
from django.http import HttpResponse
from .models import Members
from .forms import MembersForm

# Create your views here.
def index(request):
	template = 'list/index.html'
	members = Members.objects.all()
	context_dict = {'members': members}
	return render(request, template, context_dict)
def manual(request):
	template = 'list/manual.html'
	context_dict = {}
	return render(request, template, context_dict)
def add_member(request):
	template = 'list/add_member.html'
	context_dict = {}
	
	return render(request, template, context_dict)
