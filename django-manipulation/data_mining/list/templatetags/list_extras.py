from django import template
from list.models import Members
from django.http import HttpResponse

register = template.Library()

@register.inclusion_tag('list/add_member.html')
def sample(request):
	return HttpResponse('Dean')