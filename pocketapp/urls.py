from django.conf.urls import patterns, include, url

urlpatterns = patterns('pocketapp.views',
    url(r'^$', 'wechat'),
    url(r'^authorizationFinished', 'authorizationFinished'),
)