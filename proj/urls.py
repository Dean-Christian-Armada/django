from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'proj.views.home', name='home'),
    url(r'^sample/', include('sample.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
