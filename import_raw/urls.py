from django.urls import path

from . import views


app_name = "compute_graph"
urlpatterns = [
    path('', views.index, name='index'),
    path('name/', views.get_name, name="name"),
]
