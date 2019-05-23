from django.shortcuts import render, get_object_or_404
from django.views import generic

from import_raw.models import RawData


# Create your views here.

def index(request):
    return render(request, "compute_graph/index.html")

def stat_choice(request,organism):
    rawdata = get_object_or_404(RawData,organism = organism)
    return render(request, "compute_graph/stat_choice.html")

class IndexView(generic.ListView):
    template_name = "compute_graph/index.html"
    context_object_name = "organism_list"

    def get_queryset(self):
        return RawData.objects.order_by("organism")