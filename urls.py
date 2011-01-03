from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^blinddata/', include('blinddata.foo.urls')),

    #filter by country
    #(r'^(?P<alpha2_code>\w{2})/$', 'blinddata.views.index'),
    #(r'^(?P<alpha2_code>\w{2})/(?P<safe_topic>\w+)/$', 'blinddata.views.index'),
    #(r'^(?P<alpha2_code>\w{2})/(?P<safe_topic>\w+)/(?P<safe_subtopic>\w+)/$', 'blinddata.views.index'),
    #(r'^(?P<alpha2_code>\w{2})/(?P<safe_topic>\w+)/(?P<safe_subtopic>\w+)/(?P<safe_series>\w+)/$', 'blinddata.views.index'),

    # no filter
    (r'^$', 'blinddata.views.index'),
    (r'^(?P<topic_slug>[\w-]+)/$', 'blinddata.views.topic_detail'),
    (r'^(?P<topic_slug>[\w-]+)/(?P<subtopic_slug>[\w-]+)/$', 'blinddata.views.subtopic_detail'),
    (r'^(?P<topic_slug>[\w-]+)/(?P<subtopic_slug>[\w-]+)/(?P<series_code_slug>[\w-]+)/$', 'blinddata.views.series_detail'),

	#testing and development
    #(r'^crawl/$', 'blinddata.views.crawl'),
    #(r'^map/$', 'blinddata.views.map'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': '/home/thebenedict/src/blinddata/static_files'}),
    (r'^admin/', include(admin.site.urls)),
)
