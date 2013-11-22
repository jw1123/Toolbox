#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from matplotlib.pyplot import show
from os import path


class Graphdist:

    def __init__(self, song_collection, distance_collection):
        self.so = song_collection
        self.di = distance_collection
        self.savegraph()

    def savegraph(self):

        G = nx.DiGraph()

        for s in self.so.find():
            G.add_node(s['song_id'], s['metadata'])

        for d in self.di.find():
            G.add_edge(d['source'][0], d['target'][0], weight=d['weight'])

        nx.write_graphml(G, path.dirname(path.realpath("graph.py"))
                                        + '/song_comparison.graphml')
