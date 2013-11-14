#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt, concatenate
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
        #__________________________________________________________________________
        db = con.extraction_test #Change the database ######REPLACE#######
        song_test = db.song_test #Change the name of the song collection ######REPLACE#######
        distance_feat = db.distance_feat #Change the name of the distance collection ######REPLACE#######
        #__________________________________________________________________________
        self.so = song_test
        self.di = distance_feat


    def iterating(self):
        s = self.so.find(timeout=False).sort("id")
        r = self.so.find(timeout=False).sort("id")
        ski = 1
        j = 1
        for song1 in s:
            r.skip(ski)
            for song2 in r:
                distance_dict = {}
                summe, dd, ii = 0, 0, 0
                l = max(song1['metadata']['length'],song2['metadata']['length'])
                for i in song1['features']:
                    jii = 0
                    for h in song1['features'][i][0]:
                        if type(song1['features'][i][0][h]) == float:
                            a = song1['features'][i][0][h]
                            b = song2['features'][i][0][h]
                        else:
                            a = ploads(song1['features'][i][0][h])
                            b = ploads(song2['features'][i][0][h])
                        dd = self.dist(a,b)/l
                        if jii == 0:
                            distance_dict.update({i:{h:dd}})
                        else:
                            distance_dict[i].update({h:dd})
                        jii += 1
                    summe +=dd
                    ii += 1

                self.di.insert({
                    'distance_id': j,
                    'source':[song1['song_id'],song1['metadata']['title']],
                    'target':[song2['song_id'],song2['metadata']['title']],
                    'feature_distance': distance_dict,
                    'weight':summe/ii
                    })
                j += 1
            ski += 1
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
        
    def reshape(self,b,a):
        template = array([])
        new_array = []

        if b.shape[0] == a.shape[0]:
            x = b.shape[1]
            l = int(x/a.shape[1])
            for i in a:
                template = i
                for j in arange(l-1):
                    template = concatenate([template,i])
                template = concatenate([template,i[:x-len(template)]])
                new_array.append(template)
        else:
            x = b.shape[0]
            l = int(x/a.shape[0])
            for j in arange(l):
                template = concatenate([template,a])
            template = concatenate([template,a[:x-len(template)]])
            new_array.append(template)

        return linalg.norm(b-array(new_array))



