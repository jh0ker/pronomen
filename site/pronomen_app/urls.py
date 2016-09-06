from django.conf.urls import url

from . import views

app_name = 'pronomen_app'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<pronoun_id>[^/]+)/$', views.detail, name='detail'),
]
