

#Import librairies
import csv, sys, os
from py2neo import *

#Connexion à la base de données
graph = Graph("bolt://localhost:7687",auth=("neo4j","admin"))


#Fonctions parcourant le fichier csv
def taille_attribut(file):
    idx_line = 0
    with open(file) as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for row in reader :
            if idx_line == 0 :
                idx_line += 1
                return(len(row))

def index_label(file):
    idx_line = 0
    with open(file) as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for row in reader :
            if idx_line == 0 :
                for i in range (taille_attribut(file)) :
                    if row[i] == "_labels" :
                        return i
                idx_line += 1
            if idx_line > 0 :
                break


def index_type(file):
    idx_line = 0
    with open(file) as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for row in reader :
            if idx_line == 0 :
                for i in range (taille_attribut(file)) :
                    if row[i] == "_type" :
                        return i
                idx_line += 1
            if idx_line > 0 :
                break

def list_special(file):
    line = 0
    list = []
    with open(file) as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for row in reader :
            if line == 0 :
                list = row
                line += 1
            if line > 0 :
                continue
        return list

def index_special(file) :
    list = list_special(file)
    list_index = []
    idx = 0
    for i in list:
        if i == "_labels" or i == "_id" or i == "_type":
            list_index.append(idx)
        idx += 1
    return list_index

def attribut(file,row) :
    idx = list_special(file)
    dict_properties = {}
    list_index = index_special(file)
    for i in range(taille_attribut(file)):
        if i in list_index :
            continue
        if i not in list_index and row[i] != "":
            dict_properties[idx[i]] = row[i]
    return dict_properties

def check_start(file,row):
    idx_line = 0
    with open(file) as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for line in reader :
            if idx_line == 0 :
                for i in range(taille_attribut(file)):
                    if line[i] == "_start":
                        idx_start = i
                idx_line += 1
    start = row[idx_start]
    return start

def check_end(file,row):
    idx_line = 0
    with open(file) as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for line in reader :
            if idx_line == 0 :
                for i in range(taille_attribut(file)):
                    if line[i] == "_end":
                        idx_end = i
                idx_line += 1
    end = row[idx_end]
    return end




#Fonctions de créations du graphes
def create_nodes(file):
    line = 0
    dict_id = {}
    tx = graph.begin()
    with open(file) as csvfile :
        reader = csv.reader(csvfile,delimiter=",")
        for row in reader :
            if line == 0 :
                line += 1
                continue
            if line > 0 :
                if row[index_label(file)] != "":
                    properties = attribut(file,row)
                    node = Node(row[index_label(file)])
                    for property in properties :
                        node[property] = properties[property]
                    graph.create(node)
                    dict_id[row[0]] = node
    return dict_id


def create_edges(file,dict_id):
    line = 0
    tx = graph.begin()
    with open(file) as csvfile :
        reader = csv.reader(csvfile,delimiter=",")
        for row in reader :
            if line == 0 :
                line += 1
                continue
            if line > 0 :
                if row[index_type(file)] != "":
                    start = dict_id[check_start(file,row)]
                    type = row[index_type(file)]
                    end = dict_id[check_end(file,row)]
                    graph.create(Relationship(start,type,end))


#Main
def main():
    os.system('/home/jean_clement/PycharmProjects/NeOmics/media/Scripts/rankprod.R')
    dict_id = create_nodes("graph.csv")
    create_edges("graph.csv",dict_id)


if __name__ == "__main__":
    main()