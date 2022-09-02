from django.conf.urls import url
from keijiban import views

urlpatterns = [
    url('^$', views.kakikomi, name='kakikomi'),
]