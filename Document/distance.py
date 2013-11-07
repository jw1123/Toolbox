#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt
from subprocess import call
from pymongo import Connection

class Distance:

    def __init__(self):

        print "DISTANCE CALCULATION"
        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(2)
            con = Connection()
        db = con.extraction_test
        song_features = db.song_features
        distance_feat = db.distance_feat
        self.so = song_features
        self.di = distance_feat
        self.iter()          

    def iter(self):
        s = self.so.find(timeout=False) #.skip(1)
        r = self.so.find(timeout=False) #.skip(1)
        j = 1
        for song1 in s:
            for song2 in r:
                if song2['id'] > song1['id']:
                    distances = {}
                    summe, dd, ii = 0, 0, 0
                    for i in song1['features']:
                        for h in song1['features'][i]:
                            dd = self.dist(song1['features'][i][h],song2['features'][i][h])
                            distances.update({i:{h:dd}})
                            summe +=dd
                            ii += 1
                    self.di.insert({
                    'idd': j,
                    'source':[song1['id'],song1['metadata']['title']],
                    'target':[song2['id'],song2['metadata']['title']],
                    'feature_distance': distances,
                    'total':summe/ii
                    })
                    j += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def dist(self,p,q):
        if len(p) > len(q):
            d = self.reshap(p,q)
            return d
        elif len(p) < len(q):
            d = self.reshap(q,p)
            return d
        elif len(p) == len(q):
            d = self.calc(p,q)
            return d
        else:
            return "unknown"
        

    def reshap(self,p,q):
            x = len(p)/len(q)
            qi = int(x)*q
            q1 = qi + qi[0:len(p)-len(qi)]
            return self.calc(p,q1)

    def calc(self,p,q):
        c = 0
        if len(p) == len(q):
            for i in arange(len(p)):
                c += (p[i]-q[i])*(p[i]-q[i])
            dis = sqrt(c)
        else:
            dis = None
        return dis



