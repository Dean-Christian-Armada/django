from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    url(r'^$', 'data_mining.views.home', name='home'),
    url(r'^validation/', 'data_mining.views.validation', name='validation'),
    url(r'^staff/', include('list.urls', namespace='list')),
    url(r'^seamen/', include('guests.urls', namespace='guests')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', 'data_mining.views.user_logout', name='logout'),
    # url(r'^accounts/', include('registration.backends.simple.urls')),
]
