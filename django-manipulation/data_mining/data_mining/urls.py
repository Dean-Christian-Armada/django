from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    url(r'^$', 'data_mining.views.home', name='home'),
    url(r'^list/', include('list.urls', namespace='list')),
    url(r'^admin/', include(admin.site.urls)),
]
