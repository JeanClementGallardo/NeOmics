from django.urls import path

from . import views


app_name = "ImportRaw"
urlpatterns = [
    path('', views.index, name='index'),
]
