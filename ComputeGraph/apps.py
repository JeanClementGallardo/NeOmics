from django.apps import AppConfig


class ComputeGraphConfig(AppConfig):
    name = 'ComputeGraph'

    def ready(self):
        from .models import Graph
        for graph in Graph.objects.all():
            try:
                graph.start()
            except:
                pass
