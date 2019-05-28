# Import librairies
import csv, sys, os
from py2neo import *


class LoadCSV:
    def __init__(self, uri, user, password, input_file_path):
        self.graph = Graph(uri, auth=(user, password))
        self.file = input_file_path
        self.dict_id = self.create_nodes()
        self.create_edges()

    # Fonctions parcourant le fichier csv
    def index(self):
        dict_index = {}
        list_attribut = []
        line = 0
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if line == 0:
                    for i in range(len(row)):
                        if row[i] == "_labels":
                            dict_index["labels"] = i
                        elif row[i] == "_type":
                            dict_index["type"] = i
                        elif row[i] == "_start":
                            dict_index["start"] = i
                        elif row[i] == "_end":
                            dict_index["end"] = i
                        elif row[i] == "_id":
                            dict_index["id"] = i
                        else:
                            list_attribut.append(i)
                    line += 1
                if line > 0:
                    break
            dict_index["attributs"] = list_attribut
            return dict_index

    # Fonctions de créations du graphes
    def create_nodes(self):
        line = 0
        dict_id = {}
        dict_index = self.index()
        dict_attributs = {}
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if line == 0:
                    for i in range(len(row)):
                        if i in dict_index["attributs"]:
                            dict_attributs[i] = row[i]
                    line += 1
                    continue
                if line > 0:
                    if row[dict_index["labels"]] != "":
                        node = Node(row[dict_index["labels"]])
                        for i in range(len(row)):
                            if i in dict_index["attributs"] and row[i] != "":
                                node[dict_attributs[i]] = row[i]
                        self.graph.create(node)
                        dict_id[row[0]] = node
        return dict_id

    def create_edges(self):
        line = 0
        dict_index = self.index()
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if line == 0:
                    line += 1
                    continue
                if line > 0:
                    if row[dict_index["type"]] != "":
                        start = self.dict_id[row[dict_index["start"]]]
                        type = row[dict_index["type"]]
                        end = self.dict_id[row[dict_index["end"]]]
                        self.graph.create(Relationship(start, type, end))


if __name__ == "__main__":
    LoadCSV("bolt://localhost:7687", "neo4j", "admin",
            "/home/jean_clement/PycharmProjects/NeOmics/media/Scripts/sous_graph.csv")
