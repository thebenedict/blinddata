from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^blinddata/', include('blinddata.foo.urls')),
    (r'^blinddata/test/$', 'blinddata.views.test'),
    (r'^blinddata/$', 'blinddata.views.index'),
    (r'^blinddata/(?P<safe_topic>\w+)/$', 'blinddata.views.index'),
    (r'^blinddata/(?P<safe_topic>\w+)/(?P<safe_subtopic>\w+)/$', 'blinddata.views.index'),
    (r'^blinddata/(?P<safe_topic>\w+)/(?P<safe_subtopic>\w+)/(?P<safe_series>\w+)/$', 'blinddata.views.index'),
    (r'^crawl/$', 'blinddata.views.crawl'),
    (r'^map/$', 'blinddata.views.map'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': '/Users/thebenedict/django-projects/blinddata/static_files'}),
    (r'^admin/', include(admin.site.urls)),
)
