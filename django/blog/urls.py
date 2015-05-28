from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'blog.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^$', 'myblog.views.index'),
    url(
    	r'^blog/view/(?P<slug>[^\.]+).html',
    	'myblog.views.view_post',
    	name='view_blog_post' # is what we used when defining the models, get_absolute_url returns a URL automatically calculated based on the URL that is entered here
    	),
    url(
    	r'^blog/category/(?P<slug>[^\.]+).html',
    	'myblog.views.view_category',
    	name='view_blog_category'
    	),
    url(
        r'^blog/author/(?P<slug>[^\.]+).html',
        'myblog.views.view_author',
        name='view_blog_author'
        ),
)
