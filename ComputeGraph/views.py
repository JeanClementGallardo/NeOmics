from django.shortcuts import render, get_object_or_404
from django.views import generic
from .static.ComputeGraph.loadcsv import LoadCSV

from ImportRaw.models import RawData
from ComputeGraph.models import AnalysisFamily, Analysis, GraphManager, Graph
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

    for parameter in params:
        if parameter["name"] in request.POST:
            if request.POST[parameter["name"]] == "":
                error_message = "Please fill ALL the fields"
                return render(request, "ComputeGraph/stat_params.html", locals())

    if request.POST:
        return render(request, "ComputeGraph/stat_load.html", locals())

    return render(request, "ComputeGraph/stat_params.html", locals())


def stat_load(request, organism, name):
    """Execute R script and register new graph"""
    raw_data = get_object_or_404(RawData, organism=organism)
    analysis = get_object_or_404(Analysis, name=name)

    # Script execution
    working_file_path = "./"
    with open(working_file_path, 'w') as working_file:
        pass  # Execute R script with working file as output

    # Results loading on neo4j
    gm = GraphManager(request.get_host())
    graph = gm.create_graph(raw_data, analysis)
    LoadCSV(graph.neo4j_uri, graph.neo4j_user, graph.neo4j_password, working_file_path)
    return render(request, "ComputeGraph/stat_load.html")
