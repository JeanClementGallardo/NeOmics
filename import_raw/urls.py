from django.urls import path

from . import views


app_name = "import_raw"
urlpatterns = [
    path('', views.index, name='index'),
    path('name/', views.get_name, name="name"),
]
