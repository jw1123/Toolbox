#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt
from subprocess import call
from pymongo import Connection
from cPickle import loads as ploads

class Distance:

    def __init__(self):

        print "DISTANCE CALCULATION"
        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(2)
            con = Connection()
        #__________________________________________________________________________
        db = con.extraction_test #Change the database ######REPLACE#######
        song_test = db.song_test #Change the name of the song collection ######REPLACE#######
        distance_feat = db.distance_feat #Change the name of the distance collection ######REPLACE#######
        #__________________________________________________________________________
        self.so = song_test
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
                    l = song1['metadata']['length']+song2['metadata']['length']
                    for i in song1['features']:
                        try:
                            ji = 0
                            for h in song1['features'][i]:
                                try:
                                    a = ploads(song1['features'][i][h])
                                    b = ploads(song2['features'][i][h])
                                except:
                                    a = song1['features'][i][h]
                                    b = song2['features'][i][h]                              
                                dd = self.dist(a,b)/l
                                if ji == 0:
                                    distance_dict.update({i:{h:dd}})
                                else:
                                    distance_dict[i].update({h:dd})
                                ji += 1
                        except:
                            jii = 0  
                            for h in song1['features'][i][0]:
                                try:
                                    a = ploads(song1['features'][i][0][h])
                                    b = ploads(song2['features'][i][0][h])
                                except:
                                    a = song1['features'][i][0][h]
                                    b = song2['features'][i][0][h] 
                                dd = self.dist(a,b)/l
                                if jii == 0:
                                    distance_dict.update({i:{h:dd}})
                                else:
                                    distance_dict[i].update({h:dd})
                                jii += 1
                        summe +=dd
                        ii += 1

                    self.di.insert({
                    'idd': j,
                    'source':[song1['id'],song1['metadata']['title']],
                    'target':[song2['id'],song2['metadata']['title']],
                    'feature_distance': distance_dict,
                    'total':summe/ii
                    })
                    print j
                    j += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def dist(self,p,q):
        # Determine which list is longer and invoking the reshaping function
        # to even their length (otherwise we cannot compare their values)
        if type(p) == float and type(q) == float:
            return abs(p-q)
        elif p.shape > q.shape:
            d = self.reshape(p,q)
            return d
        elif p.shape < q.shape:
            d = self.reshape(q,p)
            return d
        elif p.shape == q.shape:
            d = linalg.norm(p-q)
            return d
        else:
            return "unknown"
        

    def reshape(self,p,q):
        y1, z1 = [], []
        y = p.tolist()
        z = q.tolist()
        try:
            for i in y:
                y1 += i
            for j in z:
                z1 += j
        except:
            y1 = y
            z1 = z

        # Multiply the shorter list with the smallest integer
        # to approach equal length
        x = len(y1)/len(z1)
        z2 = int(x)*z1
        # Add the remaining length of the list
        z3 = z2 + z2[0:len(y1)-len(z2)]
        z4 = array(z3).reshape(p.shape)
        return linalg.norm(p-z4)



