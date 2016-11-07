from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('main.urls')), #Main appinin urlerini burayada yazabiliriz, bu sekilde kodu yonetmesi daha kolay, main urlleri buraya da ekledik
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'},
        name='login'), #name yazdigimiz template icerisine girdigimiz action urlsindekileri ifade ediyor. template icindekiler bunlari nameleri ile taniyor
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'},
        name='logout'),

]
