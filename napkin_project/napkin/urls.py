from django.conf.urls import url
from napkin import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^(?P<group_name_slug>[\w\-]+)/$', views.group_page, name="group_page"),
    ]
