from django.shortcuts import render
from django.views import generic


from import_raw.models import RawData

# Create your views here.

def index(request):
    return render(request, "viewer/index.html")

def graph(request,organism):
    return render(request, "viewer/graph.html")

class IndexView(generic.ListView):
    template_name = "viewer/index.html"
    context_object_name = "organism_list"

    def get_queryset(self):
        return RawData.objects.order_by("organism")