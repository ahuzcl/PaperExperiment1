
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import random
import numpy
print "Hello"
import networkx as nx
import matplotlib.pyplot as plt
g = nx.Graph()
f = open("hep.txt")
edge = []
lines = f.readlines()
for line in lines :
    n = line.split()
    ns = [ int(x) for x in n ]
    nss = tuple(ns)
    g.add_nodes_from(nss)
    edge.append(nss)
    
g.add_edges_from(edge,weight =random.uniform(0,0.4))
#plt.figure(figsize=(200,200))
#nx.draw_networkx(g)
#nx.draw(g,node_size = 10)
#print "Amazon0302数据集中的节点数为："
#print g.number_of_nodes()
#print "Amazon0302数据集中的边数为："
#print g.number_of_edges()
#plt.savefig("hep.png")
#print edge
print len(g.neighbors(14))
#print type(n) 
    #g.add_edges_from(s)
#print g.number_of_nodes()
#print g.number_of_edges()
#print g.edges()