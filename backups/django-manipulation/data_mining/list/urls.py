from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
				url(r'^$', views.index, name='index'),
				url(r'^manual/$', views.manual, name='manual'),
				url(r'^delete_member/$', views.delete_member, name = 'delete_member'),
				# url(r'^update_member/$', views.update_member, name = 'update_member'),
				url(r'^search_names/$', views.search_names, name='search_names'),
				url(r'^update_form/$', views.update_form, name='update_form'),
			)