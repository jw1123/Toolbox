#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from pymongo import Connection
from matplotlib.pyplot import show

try:
    con = Connection()
except:
    call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
    sleep(2)
    con = Connection()
db = con.extraction_test 
song_test = db.song_test
distance_feat = db.distance_feat

G = nx.Graph()
labels = {}

for s in song_test.find():
    G.add_node(s['id'],s['metadata'])
    labels.update({s['id']:s['metadata']['title'].encode('utf-8').replace("'",'')})

for d in distance_feat.find():
    G.add_edge(d['source'][0],d['target'][0],length=d['total'])


nx.draw(G,nx.spring_layout(G))
nx.draw_networkx_labels(G,nx.spring_layout(G),labels)


show()