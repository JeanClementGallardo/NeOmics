from django.shortcuts import render
from django.views import generic

from ComputeGraph.models import Graph


# Create your views here.


class IndexView(generic.ListView):
    template_name = "Viewer/index.html"
    context_object_name = "graph_list"

    def get_queryset(self):
        return Graph.objects.order_by("organism__graph__analysis_family")


def graph(request, graph):
    return render(request, "Viewer/graph.html")
