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
        db = con.extraction_test #Change the database
        song_features = db.song_features #Change the name of the song collection
        distance_feat = db.distance_feat #Change the name of the distance collection
        self.so = song_features
        self.di = distance_feat
        self.iterating()          

    def iterating(self):
        s = self.so.find(timeout=False) #.skip(1)
        r = self.so.find(timeout=False) #.skip(1)
        j = 1
        for song1 in s:
            for song2 in r:
                if song2['id'] > song1['id']:
                    distance_dict = {}
                    summe, dd, ii = 0, 0, 0
                    for i in song1['features']:
                        for h in song1['features'][i]:
                            dd = self.dist(song1['features'][i][h],song2['features'][i][h])
                            distance_dict.update({i:{h:dd}})
                            summe +=dd
                            ii += 1
                    self.di.insert({
                    'idd': j,
                    'source':[song1['id'],song1['metadata']['title']],
                    'target':[song2['id'],song2['metadata']['title']],
                    'feature_distance': distance_dict,
                    'total':summe/ii
                    })
                    j += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def dist(self,p,q):
        # Determine which list is longer and invoking the reshaping function
        # to even their length (otherwise we cannot compare their values)
        if len(p) > len(q):
            d = self.reshape(p,q)
            return d
        elif len(p) < len(q):
            d = self.reshape(q,p)
            return d
        elif len(p) == len(q):
            d = self.eucl_distance(p,q)
            return d
        else:
            return "unknown"
        

    def reshape(self,p,q):
        # Multiply the shorter list with the smallest integer
        # to approach equal length
        x = len(p)/len(q)
        qi = int(x)*q
        # Add the remaining length of the list
        q1 = qi + qi[0:len(p)-len(qi)]
        return self.eucl_distance(p,q1)

    def eucl_distance(self,p,q):
        c = 0
        # Calculation of euclidean distance
        if len(p) == len(q):
            for i in arange(len(p)):
                c += (p[i]-q[i])*(p[i]-q[i])
            dis = sqrt(c)
        else:
            dis = None
        return dis



