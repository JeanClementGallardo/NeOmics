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
    @property
    def attributes_length(self):
        idx_line = 0
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if idx_line == 0:
                    idx_line += 1
                    return len(row)

    @property
    def label_index(self):
        idx_line = 0
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if idx_line == 0:
                    for i in range(self.attributes_length):
                        if row[i] == "_labels":
                            return i
                    idx_line += 1
                if idx_line > 0:
                    break

    @property
    def type_index(self):
        idx_line = 0
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if idx_line == 0:
                    for i in range(self.attributes_length):
                        if row[i] == "_type":
                            return i
                    idx_line += 1
                if idx_line > 0:
                    break

    def list_special(self):
        line = 0
        specials = []
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if line == 0:
                    specials = row
                    line += 1
                if line > 0:
                    continue
            return specials

    def index_special(self):
        list = self.list_special()
        list_index = []
        idx = 0
        for i in list:
            if i == "_labels" or i == "_id" or i == "_type":
                list_index.append(idx)
            idx += 1
        return list_index

    def attribut(self, row):
        idx = self.list_special()
        dict_properties = {}
        list_index = self.index_special()
        for i in range(self.attributes_length):
            if i in list_index:
                continue
            if i not in list_index and row[i] != "":
                dict_properties[idx[i]] = row[i]
        return dict_properties

    def check_start(self, row):
        idx_line = 0
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for line in reader:
                if idx_line == 0:
                    for i in range(self.attributes_length):
                        if line[i] == "_start":
                            idx_start = i
                    idx_line += 1
        start = row[idx_start]
        return start

    def check_end(self, row):
        idx_line = 0
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for line in reader:
                if idx_line == 0:
                    for i in range(self.attributes_length):
                        if line[i] == "_end":
                            idx_end = i
                    idx_line += 1
        end = row[idx_end]
        return end

    # Fonctions de créations du graphes
    def create_nodes(self):
        line = 0
        dict_id = {}
        tx = self.graph.begin()
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if line == 0:
                    line += 1
                    continue
                if line > 0:
                    if row[self.label_index] != "":
                        properties = self.attribut(row)
                        node = Node(row[self.label_index])
                        for property in properties:
                            node[property] = properties[property]
                        self.graph.create(node)
                        dict_id[row[0]] = node
        return dict_id

    def create_edges(self):
        line = 0
        tx = self.graph.begin()
        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if line == 0:
                    line += 1
                    continue
                if line > 0:
                    if row[self.type_index] != "":
                        start = self.dict_id[self.check_start(row)]
                        type = row[self.type_index]
                        end = self.dict_id[self.check_end(row)]
                        self.graph.create(Relationship(start, type, end))


if __name__ == "__main__":
    LoadCSV("bolt://localhost:7687", "neo4j", "admin", "path_to_csv")
