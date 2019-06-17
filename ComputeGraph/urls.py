# !/usr/bin/env python3
"""Describes ComputeGraph urls, and link them with views"""
__authors__ = ["Eliot Ragueneau", "Jean-Clément Gallardo"]
__date__ = "14/06/2019"
__email__ = "eliot.ragueneau@etu.u-bordeaux.fr"

from django.urls import path

from . import views

app_name = "ComputeGraph"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<project_name>', views.StatView.as_view(), name='stat_choice'),
    path('<project_name>/<analysis_name>', views.stat_params, name='stat_params'),
    path('<project_name>/<analysis_name>/stat_load', views.stat_load, name='stat_load'),
]
