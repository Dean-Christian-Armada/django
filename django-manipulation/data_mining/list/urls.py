from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
				url(r'^$', views.index, name='index'),
				url(r'^manual/$', views.manual, name='manual'),
				url(r'^delete_member/$', views.delete_member, name = 'delete_member'),
				url(r'^restore_member/$', views.restore_member, name = 'restore_member'),
				# url(r'^update_member/$', views.update_member, name = 'update_member'),
				url(r'^search_names/$', views.search_names, name='search_names'),
				url(r'^update_form/$', views.update_form, name='update_form'),
				url(r'^view_cert/$', views.view_cert, name='view_cert'),
				url(r'^trash/$', views.trash, name='trash'),
				url(r'^recycle_bin/$', views.recycle_bin, name='recycle_bin'),
			)