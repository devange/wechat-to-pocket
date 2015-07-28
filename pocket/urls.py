from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pocket.views.home', name='home'),
    # url(r'^pocket/', include('pocket.foo.urls')),
    url(r'^', include('pocketapp.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

import pocket.settings

if not pocket.settings.DEBUG:  
	urlpatterns += patterns('',
		url(r'^statics/(?P<path>.*)$', 'django.views.static.serve', {'document_root': pocket.settings.STATIC_ROOT}),
	)  