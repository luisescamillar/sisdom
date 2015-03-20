from django.conf.urls import patterns, url
from app import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^registro/$', views.register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        url(r'^profile/$', views.editar, name='editar'),
        url(r'^open/$', views.open, name='open'),
        url(r'^config/$', views.config, name='config'),
)
