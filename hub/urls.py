from django.urls import path

from . import views

app_name = 'hub'
urlpatterns = [
    path("", views.index, name="index"),
]
