from django.shortcuts import render, get_object_or_404
from django.views import generic

from ImportRaw.models import RawData
from ComputeGraph.models import AnalysisFamily, Analysis, Graph
from .static.ComputeGraph.results_to_neo4j import ResultsToNeo4j
import json


# Create your views here.
class IndexView(generic.ListView):
    template_name = "ComputeGraph/index.html"
    context_object_name = "organism_list"

    def get_queryset(self):
        return RawData.objects.order_by("organism")


class StatView(generic.ListView):
    template_name = "ComputeGraph/stat_choice.html"
    context_object_name = "families"

    def get_queryset(self):
        return AnalysisFamily.objects.order_by("name")


def stat_params(request, organism, name):
    analysis = get_object_or_404(Analysis, name=name)
    raw_data = get_object_or_404(RawData, organism=organism)
    with open(analysis.parameters_json_file.path, 'r') as param_file:
        params = json.load(param_file)

    return render(request, "ComputeGraph/stat_params.html", locals())


def stat_load(request, organism, name):
    """Execute R script and register new graph"""
    raw_data = get_object_or_404(RawData, organism=organism)
    analysis = get_object_or_404(Analysis, name=name)

    with open(analysis.parameters_json_file.path, 'r') as param_file:
        params = json.load(param_file)

    for parameter in params:
        if parameter["name"] in request.POST:
            if request.POST[parameter["name"]] == "":
                error_message = "Please fill ALL the fields"
                return render(request, "ComputeGraph/stat_params.html", locals())

    if request.POST:
        graph = Graph.create(request.get_host(), raw_data, analysis.family)
        # TODO Execute R script with R params
        # TODO Make R output in tmp directory
        ResultsToNeo4j(graph.uri, graph.user, graph.password,
                       "/home/eliot/Documents/Travail/M1/Projets/NeOmics/Organism__Arabidopsis")
        # TODO remove tmp results directory
        return render(request, "ComputeGraph/stat_load.html")

    return render(request, "ComputeGraph/stat_load.html")