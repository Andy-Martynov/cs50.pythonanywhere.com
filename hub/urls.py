from django.urls import path

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = 'hub'
urlpatterns = [
    path("", views.index, name="index"),
    path("hello/<str:text>", views.hello, name="hello"),
    path("beam_hello", views.beam_hello, name="beam_hello"),
    path("beam_hello/<str:text>", views.beam_hello, name="beam_hello"),
    path("beam_user_message/<int:id>", views.beam_user_message, name="beam_user_message"),

    path('pusher/auth', views.pusher_auth, name='pusher_auth'),
    path('pusher/beams-auth', views.pusher_beams_auth, name='pusher_beams_auth'),
    path('pusher/beams-auth/<int:user_id>', views.pusher_beams_auth, name='pusher_beams_auth'),

    path("post_create", views.PostCreate.as_view(), name="post_create"),
    path("post_create/<str:anchor>", views.PostCreate.as_view(), name="post_create"),
    path("post_update/<int:pk>", views.PostUpdate.as_view(), name="post_update"),
    path("post_delete/<int:id>", views.post_delete, name="post_delete"),

    url(r'^service-worker(.*.js)$',
        TemplateView.as_view(template_name='hub/service-worker.js',
            content_type='application/x-javascript'))
]
