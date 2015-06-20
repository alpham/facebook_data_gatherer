from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'frontend.views.home', name='home'),
]