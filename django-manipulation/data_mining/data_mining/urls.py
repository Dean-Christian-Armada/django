from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

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

# Enables Media
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)