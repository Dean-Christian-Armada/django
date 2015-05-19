from django.shortcuts import render
from django.http import HttpResponse

def home(request):
	context_dict = {}
	template = 'index.html'
	# return HttpResponse('Homepage'
	return render(request, template, context_dict)