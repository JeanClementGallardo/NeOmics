from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404
from ComputeGraph.models import Graph
import py2neo as neo

from string import ascii_lowercase
import itertools


# Create your views here.


class IndexView(generic.ListView):
    template_name = "Viewer/index.html"
    context_object_name = "graph_list"

    def get_queryset(self):
        return Graph.objects.order_by("organism__graph__analysis_family")


def graph(request, graph):
    graph = get_object_or_404(Graph, name=graph)
    return render(request, "Viewer/graph.html", locals())


class ImportGraph:
    query = ""
    nodes = []

    def add_node(self):
        pass

    @staticmethod
    def id_generator():
        """Generate id by alphabetical order"""
        for size in itertools.count(1):
            for s in itertools.product(ascii_lowercase, repeat=size):
                yield "".join(s)

    def update_global_query(self):
        ids = self.id_generator()
        matches = "MATCH "
        returned = " RETURN "
        return_sth = False
        for node in self.nodes:
            matches += "("
            if node.returned.get() == 1:
                node_id = next(ids)
                matches += "{}".format(node_id)
                returned += "{}, ".format(node_id)
                return_sth = True
            if node.node_type:
                matches += ":{}".format(node.node_type)
            if node.name.get() != "":
                matches += ' {{name: "{}" }}'.format(node.name.get())
            matches += ")"

            link = node.link
            if link:
                link.update_type_list()
                matches += "-["
                if link.simple:
                    link_type = link.type
                    if link.returned.get() == 1:
                        link_id = next(ids)
                        matches += "{}".format(link_id)
                        returned += "{}, ".format(link_id)
                        return_sth = True
                    if link_type:
                        matches += ":{}".format(link_type)
                else:
                    matches += "*{}..{}".format(link.min, link.max)
                matches += "]-"

        if return_sth:
            returned = returned[:-2]
        self.query = matches + returned

    class Node:
        def __init__(self):
            ImportGraph.nodes.append(self)

            self.node_type = ""
            self.returned = False
            self.name_options = []
            self.name = ""
            self.link = None
            self.next = None

        @property
        def descriptor(self):
            cypher = "("
            if self.node_type:
                cypher += ":{}".format(self.node_type)
            if self.name != "":
                cypher += ' {{name: "{}" }}'.format(self.name)
            return cypher + ")"

        @property
        def query(self):
            cypher = "MATCH "
            for node in ImportGraph.nodes:
                if node is self:
                    break
                cypher += node.descriptor

                link = node.link
                if link:
                    link.update_type_list()
                    cypher += "-["
                    if link.simple:
                        link_type = link.type
                        if link_type:
                            cypher += ":{}".format(link_type)
                    else:
                        cypher += "*{}..{}".format(link.min, link.max)
                    cypher += "]-"
            return cypher

        def display_types(self):
            """Display a node selection panel and set buttons to choose the type of node"""
            # TODO Fix the gap between MORCEAU and inner_frame
            # TODO Fix the gap between link and next line
            types_query = self.query + "(a) RETURN DISTINCT labels(a) as type"
            types = [result['type'][-1] for result in neo_graph.run(types_query)]
            types.append("Unknown")

        def select_type(self, node_type):
            """Select a type from the node selection panel previously built and destroy it"""
            # Set node_type variable used after
            self.node_type = node_type if node_type != "Unknown" else ""

            # Update autocompletion list since the type has been set
            self.update_name_list()
            ImportGraph.update_global_query(ImportGraph())

        def update_name_list(self):
            """Set the autocompletion list accordingly to current node information"""
            name_query = self.query + '(a'
            if self.node_type:
                name_query += ":{}".format(self.node_type)
            name_query += ') RETURN a.name'
            # completion list is a set to avoid repetition
            completion_set = {result['a.name'] for result in neo_graph.run(name_query) if
                              result['a.name'] is not None}
            self.name_box.set_completion_list(completion_set)

        def new_node(self):
            """Add a new node to the list"""
            self.add_button.grid_forget()
            self.link = Relation(self)
            self.link.next.update_name_list()
            update_global_query()

    class Relation:
        """A relation is a link between two ndoes. It can be either simple or composed.
        A simple relation is a simple link between two adjacents nodes.
        A composed relation have a determined number of relations to travel through to reach the next node"""

        def __init__(self, previous: Node):
            self.simple = True

            self.returned = False

            self.type = ""
            self.type_options = []

            self.min = 0
            self.max = 0

            self.previous = previous
            self.next = ImportGraph.nodes
            self.update_type_list()

        def update_type_list(self):
            """Updates type autocompletion list """
            type_query = self.previous.query + self.previous.descriptor + '-[r]-{} RETURN DISTINCT type(r) as types'.format(
                self.next.descriptor)
            completion_list = {result['types'] for result in neo_graph.run(type_query) if
                               result['types'] is not None}
            print(type_query)
            print(completion_list)
            self.type_box.set_completion_list(completion_list)

        def switch(self):
            """Switch between simple and composed relation"""
            if self.simple:
                self.simple = False
            else:
                self.simple = True
            ImportGraph.update_global_query(ImportGraph())

        def update_max(self):
            """Update max spinner value if min value is greater"""
            if self.max < self.min:
                self.max = self.min

        def update_min(self):
            """Update min spinner value if max value is lower"""
            if self.max < self.min:
                self.min = self.max

    init = Node()
    init.update_name_list()
    update_global_query()
    root.mainloop()
