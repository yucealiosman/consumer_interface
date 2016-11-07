# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'main'
urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
    url(r'^rooms/(?P<hotel_code>[\w-]+)', views.rooms, name='rooms'),
    url(r'^hotels/$', views.hotels, name='hotels'),
    url(r'^room/(?P<product_code>[\w-]+)', views.room, name='room'),
    url(r'^book/$', views.book, name='book'),
    url(r'^confirmation/(?P<confirmation_code>[\w-]+)', views.confirmation,
        name='confirmation'),
    url(r'^mybookings/$', views.mybookings, name='mybookings'),

]
