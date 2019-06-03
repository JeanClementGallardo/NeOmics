import os
import py2neo
import py2neo.matching
import csv
from pathlib import Path
from typing import *


def extract_node(node_descriptor: str) -> Tuple[List[str], str, str]:
    """Extract node info from standardized node descriptor that can be seen in csv files or in file names

    :param node_descriptor: String like label1__label2__nameOfNode(RELATION_TO_ABOVE_NODE)
    :return: List of labels of node, name of node, relation type to above node
    """
    labels = []
    rel_type = "RELATION"

    if "__" in node_descriptor:
        labels = node_descriptor.split('__')
        name = labels.pop()
    else:
        name = node_descriptor

    if '(' in name:
        rel_type = name[name.find('(') + 1: name.find(')')]
        name = name.split('(')[0]

    return labels, name, rel_type


class ResultsToNeo4j:
    def __init__(self, uri, user, password, root_path):
        self.graph = py2neo.Graph(uri=uri, auth=(user, password))
        self.tx = self.graph.begin()
        self.nodes = [node for node in self.graph.nodes.match()]
        self.__rec_browse_dir(Path(root_path), None)
        self.tx.commit()

    def get_or_create_node(self, *labels, **properties) -> py2neo.Node:
        # TODO Optimize searching
        for node in self.nodes:
            if node.labels == labels and dict(node) == properties:
                return node
        node = py2neo.Node(*labels, **properties)
        self.tx.create(node)
        self.nodes.append(node)
        return node

    def create_node(self, *labels, **properties):
        node = py2neo.Node(*labels, **properties)
        self.tx.create(node)
        self.nodes.append(node)

        return node

    def __rec_browse_dir(self, path: Path, previous_node):
        labels, name, rel_type = extract_node(path.stem)

        current_node = self.create_node(*labels, name=name)

        if previous_node:
            self.tx.merge(py2neo.Relationship(previous_node, rel_type, current_node))

        if path.is_dir():
            for elt in path.iterdir():
                self.__rec_browse_dir(elt, current_node)

        if path.is_file():
            if path.suffix == ".csv":
                with path.open() as csv_file:
                    sample = csv_file.read(1024)
                    dialect = csv.Sniffer().sniff(sample)
                    csv_file.seek(0)
                    reader = csv.reader(csv_file, dialect)
                    # if csv.Sniffer().has_header(sample):
                    header = next(reader, None)
                    col_to_node = {}
                    for col in range(len(header)):
                        sub_labels, sub_name, sub_rel = extract_node(header[col])
                        sub_node = self.create_node(*sub_labels, name=sub_name)
                        self.tx.merge(py2neo.Relationship(current_node, sub_rel, sub_node))
                        col_to_node[col] = sub_node

                    for row in reader:
                        for col in range(len(row)):
                            if row[col] != "":
                                sub_sub_labels, sub_sub_name, sub_sub_rel = extract_node(row[col])
                                sub_sub_node = self.get_or_create_node(*sub_sub_labels, name=sub_sub_name)
                                self.tx.merge(py2neo.Relationship(col_to_node[col], sub_sub_rel, sub_sub_node))
                    # else:
                    #     raise NotImplementedError("CSV without header")
            else:
                raise NotImplementedError("No CSV File")
