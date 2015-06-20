from django.conf.urls import url

urlpatterns = [
    url(r'^file/$', 'classify.views.classify_file', name='file'),
    url(r'^sentence/$', 'classify.views.classify_sentence', name='sentence'),
    url(r'^post/$', 'classify.views.classify_post', name='post'),

]
