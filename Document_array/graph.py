#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from pymongo import Connection
from matplotlib.pyplot import show
from os import path

try:
    con = Connection()
except:
    call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
    sleep(2)
    con = Connection()
db = con.extraction_test 
song_test = db.song_test
distance_feat = db.distance_feat

G = nx.DiGraph()

for s in song_test.find():
    G.add_node(s['song_id'],s['metadata'])      #title=s['metadata']['title'],album=s['metadata']['album'],\
                                                #artist=s['metadata']['artist'],year=s['metadata']['year'],genre=s['metadata']['genre'])
    

for d in distance_feat.find():
    G.add_edge(d['source'][0],d['target'][0],weight=d['weight'])


#nx.draw(G)
#show()

nx.write_graphml(G, path.dirname(path.realpath("graph.py"))+'/distance.graphml')
