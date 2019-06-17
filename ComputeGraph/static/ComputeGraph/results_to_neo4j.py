# !/usr/bin/env python3
"""Grants a class that interprets R analysis outputs as a folder tree, which contains node descriptor
explained in extract_node()"""
__authors__ = ["Eliot Ragueneau", "Jean-Clément Gallardo"]
__date__ = "14/06/2019"
__email__ = "eliot.ragueneau@etu.u-bordeaux.fr"

import csv
import re
from pathlib import Path
from typing import *

import py2neo
import py2neo.matching


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
        self.relations = [rel for rel in self.graph.relationships.match()]
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

    def get_or_create_relation(self, relation: py2neo.Relationship):
        for rel in self.relations:
            if rel == relation:
                return rel
        self.tx.merge(relation)
        self.relations.append(relation)
        return relation

    def create_node(self, *labels, **properties):
        node = py2neo.Node(*labels, **properties)
        self.tx.create(node)
        self.nodes.append(node)

        return node

    def get_node_by_property(self, *properties_values):
        for node in self.nodes:
            if set(properties_values).issubset(set(dict(node).values())):
                return node
        return None

    def add_relation(self, prop_a, prop_b, rel_type: str):
        node_a = self.get_node_by_property(prop_a)
        if node_a:
            node_b = self.get_node_by_property(prop_b)
            if node_b:
                self.tx.merge(py2neo.Relationship(node_a, rel_type, node_b))

    def __rec_browse_dir(self, path: Path, previous_node):
        labels, name, rel_type = extract_node(path.stem)

        current_node = self.get_or_create_node(*labels, name=name)

        if previous_node:
            self.get_or_create_relation(py2neo.Relationship(previous_node, rel_type, current_node))

        if path.is_dir():
            for elt in path.iterdir():
                self.__rec_browse_dir(elt, current_node)

        if path.is_file():
            if path.suffix == ".csv":
                with path.open() as file:
                    sample = file.read(1024)
                    dialect = csv.Sniffer().sniff(sample)
                    file.seek(0)
                    reader = csv.reader(file, dialect)
                    header = next(reader, None)
                    col_to_node = {}
                    for col in range(len(header)):
                        sub_labels, sub_name, sub_rel = extract_node(header[col])
                        sub_node = self.create_node(*sub_labels, name=sub_name)
                        self.get_or_create_relation(py2neo.Relationship(current_node, sub_rel, sub_node))
                        col_to_node[col] = sub_node

                    for row in reader:
                        for col in range(len(row)):
                            if row[col] != "":
                                sub_sub_labels, sub_sub_name, sub_sub_rel = extract_node(row[col])
                                sub_sub_node = self.get_or_create_node(*sub_sub_labels, name=sub_sub_name)
                                self.get_or_create_relation(
                                    py2neo.Relationship(col_to_node[col], sub_sub_rel, sub_sub_node))

            elif path.suffix == ".lab":
                label = path.stem
                with path.open() as file:
                    for name in file:
                        node = self.get_node_by_property(name)  # TODO Find a way to generalize GOI labels and TF labels
                        if node is not None:
                            node.update_labels(node.labels + [label])
                            self.tx.push(node)

            elif path.suffix == ".rel":
                sep = re.compile('[\t|,; ]')
                with path.open() as file:
                    for line in file:
                        line.strip()
                        relation = sep.split(line)
                        self.add_relation(*relation[:3])


            else:
                raise NotImplementedError("No CSV File")
