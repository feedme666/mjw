from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url('keijiban/', include('keijiban.urls')),
    url(r'^admin/', admin.site.urls),
]