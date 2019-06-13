from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import generic

from ComputeGraph.models import Graph


# Create your views here.

class IndexView(generic.ListView):
    template_name = "Viewer/index.html"
    context_object_name = "graph_list"

    def get_queryset(self):
        return Graph.objects.order_by("project__graph__analysis_family")


def graph(request, graph):
    graph = get_object_or_404(Graph, name=graph)
    return render(request, "Viewer/graph.html", locals())
