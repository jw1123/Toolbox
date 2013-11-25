#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import linalg, array, arange, sqrt, concatenate
from time import sleep


class Distance:

    def __init__(self, song_collection, distance_collection):

        print "DISTANCE CALCULATION"
        #___________________________________________________
        # Change the coefficients for the features you chose
        coeff = [0.25, 0.25, 0.25, 0.25]   # ###REPLACE####
        #___________________________________________________
        self.so = song_collection
        self.di = distance_collection

        self.iterating(coeff)

        #for d in distance_feat.find(): print d

    def iterating(self, coeff):
        s = self.so.find(timeout=False) #.sort("song_id")
        r = self.so.find(timeout=False) #.sort("song_id")
        ski = 1
        j = 1
        for song1 in s:
            r.skip(ski)
            for song2 in r:
                if song1['features'].sort() == song2['features'].sort():
                    distance_dict, weight = self.browse_features(song1, song2, coeff)
                    self.di.insert({
                        'distance_id': j,
                        'source': [song1['song_id'], song1['metadata']['title']],
                        'target': [song2['song_id'], song2['metadata']['title']],
                        'feature_distance': distance_dict,
                        'weight': weight})
                    print j
                    j += 1
                else:
                    print "Songs need to have the same features"
                    print song1['metadata']['title'], " and ", song2['metadata']['title'], " do not match."
            ski += 1
            r.rewind()
        print "Distance calculation successfully completed!"

    def browse_features(self, song1, song2, coeff):
        distance_dict = {}
        summe, dd, ddd, ii = 0, 0, 0, 0
        l = max(song1['metadata']['length'],
                song2['metadata']['length'])
        # Parsing through all features
        for i in song1['features']:
            jii = 0
            # Parsing through all parameter "names"
            for k in arange(len(song1['features'][i])):
                for h in song1['features'][i][k]:
                    a = song1['features'][i][k][h]['data']
                    b = song2['features'][i][k][h]['data']
                    dd = self.dist(a, b)/l
                    if i == 'MelFrequencyCepstrum':
                        ddd = coeff[0]*dd
                    elif i == 'LinearPower':
                        ddd = coeff[1]*dd
                    elif i == 'BPM':
                        ddd = coeff[2]*dd
                    elif i == 'Chromagram':
                        ddd = coeff[3]*dd
                    else:
                        ddd = dd
                    if jii == 0:
                        distance_dict.update({i: [{h: dd}]})
                    else:
                        distance_dict[i].append({h: dd})
                    jii += 1
                    summe += ddd
                    ii += 1
        return distance_dict, summe/ii

    def dist(self, x, y):
        # Determine which list is longer and invoking the reshaping function
        # to even their length (otherwise we cannot compare their values)
        p = array(x)
        q = array(y)

        if type(p) == float and type(q) == float:
            return abs(p-q)
        elif p.shape > q.shape:
            d = self.reshape(p, q)
            return d
        elif p.shape < q.shape:
            d = self.reshape(q, p)
            return d
        elif p.shape == q.shape:
            d = linalg.norm(p-q)
            return d
        else:
            return "unknown"

    def reshape(self, b, a):
        template = array([])
        new_array = []

        if b.shape[0] == a.shape[0]:
            x = b.shape[1]
            l = int(x/a.shape[1])
            for i in a:
                template = i
                for j in arange(l-1):
                    template = concatenate([template, i])
                template = concatenate([template, i[:x-len(template)]])
                new_array.append(template)
        else:
            x = b.shape[0]
            l = int(x/a.shape[0])
            for j in arange(l):
                template = concatenate([template, a])
            template = concatenate([template, a[:x-len(template)]])
            new_array.append(template)

        return linalg.norm(b-array(new_array))
