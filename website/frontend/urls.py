from django.conf.urls import patterns, url

urlpatterns = patterns(
    url('^$', '.views.home', name='home')
)