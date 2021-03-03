from django.urls import path
from . import views

app_name = 'react'
urlpatterns = [
    path("", views.index, name="index"),
]