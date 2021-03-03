from django.urls import path
from . import views

app_name = 'vue'
urlpatterns = [
    path("", views.index, name="index"),
]