from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from polls.models import Question, Choice
from django.core.urlresolvers import reverse
from django.views import generic


# Create your views here.
def home(request):
	return render(request, 'home.html')