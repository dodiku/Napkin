from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/admin/', admin.site.urls),
    url(r'^', include('napkin.urls')),

]
