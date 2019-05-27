from django.shortcuts import render, get_object_or_404
from django.views import generic

from import_raw.models import RawData
from compute_graph.models import AnalysisFamily, Analysis
import json


# Create your views here.

def index(request):
    return render(request, "compute_graph/index.html")


def stat_choice(request, organism):
    rawdata = get_object_or_404(RawData, organism=organism)
    return render(request, "compute_graph/stat_choice.html")


def stat_params(request, organism, name):
    analysis = get_object_or_404(Analysis, name=name)
    # family = get_object_or_404(AnalysisFamily)
    # family.analysis_set.all()
    raw_data = get_object_or_404(RawData, organism=organism)
    with open(analysis.parameters_json_file.path, 'r') as param_file:
        params = json.load(param_file)

    for parameter in params:
        if parameter["name"] in request.POST:
            if request.POST[parameter["name"]] == "":
                error_message = "Please fill ALL the fields"
                return render(request, "compute_graph/stat_params.html", locals())

    return render(request, "compute_graph/stat_params.html", locals())


class IndexView(generic.ListView):
    template_name = "compute_graph/index.html"
    context_object_name = "organism_list"

    def get_queryset(self):
        return RawData.objects.order_by("organism")


class StatView(generic.ListView):
    template_name = "compute_graph/stat_choice.html"
    context_object_name = "families"

    def get_queryset(self):
        return AnalysisFamily.objects.order_by("name")