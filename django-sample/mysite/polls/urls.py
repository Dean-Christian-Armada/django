from django.conf.urls import url
from . import views

urlpatterns = [
					# ex: /polls/
					#url(r'^$', views.index, name='index'),
					url(r'^$', views.IndexView.as_view(), name='index'),
					# ex: /polls/5/
					#url(r'^(?P<question_id>[0-9]+)/$', views.details, name='details'),
					url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='details'),
					# ex: /polls/5/results/
					#url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
					url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
					# ex: /polls/5/vote/
					url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
				]