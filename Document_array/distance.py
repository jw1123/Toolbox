#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt, concatenate
from subprocess import call
from pymongo import Connection
from time import sleep

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
        coeff = [0.2,0.2,0.2,0.2,0.2]
        self.iterating(coeff)

        #for d in distance_feat.find(): print d


    def iterating(self,coeff):
        s = self.so.find(timeout=False).limit(80).sort("song_id")
        r = self.so.find(timeout=False).limit(80).sort("song_id")
        ski = 1
        j = 1
        for song1 in s:
            r.skip(ski)
            for song2 in r:
                distance_dict = {}
                summe, dd, ddd, ii = 0, 0, 0, 0
                l = max(song1['metadata']['length'],song2['metadata']['length'])
                for i in song1['features']:
                    jii = 0
                    for j in arange(len(song1['features'][i])):
                        for h in song1['features'][i][j]:
                            a = song1['features'][i][j][h]['data']
                            b = song2['features'][i][j][h]['data']
                            dd = self.dist(a,b)/l
                            if i == 'MelFrequencyCepstrum': ddd = coeff[0]*dd
                            elif i == 'LinearPower': ddd = coeff[1]*dd
                            elif i == 'BPM': ddd = coeff[2]*dd
                            elif i == 'Chromagram': ddd = coeff[3]*dd
                            elif i == 'RMS': ddd = coeff[4]*dd
                            else: ddd = dd
                            if jii == 0:
                                distance_dict.update({i:{h:dd}})
                            else:
                                distance_dict[i].update({h:dd})
                            jii += 1
                        summe +=ddd
                        ii += 1
                self.di.insert({
                    'distance_id': j,
                    'source':[song1['song_id'],song1['metadata']['title']],
                    'target':[song2['song_id'],song2['metadata']['title']],
                    'feature_distance': distance_dict,
                    'weight':summe/ii
                    })
                print j
                j += 1
            ski += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def dist(self,x,y):
        # Determine which list is longer and invoking the reshaping function
        # to even their length (otherwise we cannot compare their values)
        p = array(x)
        q = array(y)

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



