from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^', include('napkin.urls')),
    url(r'^admin/admin/', admin.site.urls),

]
