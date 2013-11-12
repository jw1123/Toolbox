#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt, concatenate
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
                    l = max(song1['metadata']['length'],song2['metadata']['length'])
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
                    j += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def dist(self,p,q):
        # Determine which list is longer and invoking the reshaping function
        # to even their length (otherwise we cannot compare their values)

        if p.shape > q.shape:
            d = self.reshape(p,q)
            return d
        elif p.shape < q.shape:
            d = self.reshape(q,p)
            return d
        elif type(p) == float and type(q) == float:
            return abs(p-q)
        elif p.shape == q.shape:
            d = linalg.norm(p-q)
            return d
        else:
            return "unknown"
        
    def reshape(self,b,a):
        x = b.shape[1]

        l = int(x/a.shape[1])
        template = array([])
        new_array = []

        for i in a:
            template = i
            for j in arange(l-1):
                template = concatenate([templa,i])
            template = concatenate([templa,i[:len(templa)-x]])
            new_array.append(templa)

        return linalg.norm(b-array(new_array))



