# !/usr/bin/env python3
__authors__ = ["Eliot Ragueneau", "Jean-Clément Gallardo"]
__date__ = "14/06/2019"
__email__ = "eliot.ragueneau@etu.u-bordeaux.fr"
import json
import os
import threading
from shutil import rmtree
from typing import *

from django.shortcuts import render, get_object_or_404
from django.views import generic

from ComputeGraph.models import AnalysisFamily, Analysis, Graph
from ImportRaw.models import Project
from NeOmics import settings
from .static.ComputeGraph.results_to_neo4j import ResultsToNeo4j


# Create your views here.
class IndexView(generic.ListView):
    template_name = "ComputeGraph/index.html"
    context_object_name = "project_list"

    def get_queryset(self):
        return Project.objects.order_by("name")


class StatView(generic.ListView):
    template_name = "ComputeGraph/stat_choice.html"
    context_object_name = "families"

    def get_queryset(self):
        return AnalysisFamily.objects.order_by("name")


def stat_params(request, project_name, analysis_name):
    project = get_object_or_404(Project, name=project_name)
    analysis = get_object_or_404(Analysis, name=analysis_name)
    with open(analysis.parameters_json_file.path, 'r') as param_file:
        params = json.load(param_file)

    return render(request, "ComputeGraph/stat_params.html", locals())


def stat_load(request, project_name, analysis_name):
    """Execute R script and register new graph"""
    project = get_object_or_404(Project, name=project_name)
    analysis = get_object_or_404(Analysis, name=analysis_name)

    with open(analysis.parameters_json_file.path, 'r') as param_file:
        params = json.load(param_file)

    for parameter in params:
        if parameter["name"] in request.POST:
            if request.POST[parameter["name"]] == "":
                error_message = "Please fill ALL the fields"
                return render(request, "ComputeGraph/stat_params.html", locals())

    if request.POST:
        graph = Graph.create(request.get_host(), project, analysis.family)
        parameters = {parameter["name"]: request.POST[parameter["name"]] for parameter in params}
        process_thread = threading.Thread(target=process_analysis, args=(graph, analysis, parameters))
        process_thread.start()
        return render(request, "ComputeGraph/stat_load.html")

    return render(request, "ComputeGraph/stat_load.html")


def process_analysis(graph: Graph, analysis: Analysis, parameters: Dict):
    tmp_dir = "{}/tmp/{}_on_{}".format(settings.MEDIA_ROOT, graph.project.name, analysis.name)
    os.mkdir(tmp_dir)
    analysis.execute(out_dir=tmp_dir, **parameters)
    ResultsToNeo4j(graph.uri, graph.user, graph.password, tmp_dir)
    # Remove tmp files
    rmtree(tmp_dir)
    return "Completed"
