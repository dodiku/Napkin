from django.conf.urls import url
from napkin import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^feedback/$', views.feedback, name="feedback"),
    url(r'^about/$', views.about, name="about"),
    url(r'^(?P<group_name_slug>[\w\-]+)/$', views.group_page, name="group_page"),
    url(r'^click/(?P<click_id>[\w\-]+)/$', views.post_click, name="post_click"),
    ]
