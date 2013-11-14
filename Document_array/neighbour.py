#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import Connection
from numpy import arange
from os import path
from subprocess import call


class Neighbour:

    def __init__(self):
        try:
            con = Connection()
        except:
            call(["osascript", "-e", 'tell app "Terminal" to do script "mongod"'])
            sleep(2)
            con = Connection()
        #________________________
        db = con.extraction_test #Change the name of the database ######REPLACE#######
        #_________________________
        d = db.distance_feat.find()
        s = db.song_test.find()

        pa = path.realpath("neighbour.py")
        call(["mkdir", pa[:len(pa)-len("neighbour.py")] + "test/"])
        call(["touch", pa[:len(pa)-len("neighbour.py")] + "test/test.txt"])
        f = open(pa[:len(pa)-len("neighbour.py")] + "test/test.txt",'w') 

        for song in s:
            mini, maxi = self.minmax(song['song_id'],d,3)
            d.rewind()
            self.write_neighbours(song['song_id'],mini,maxi,f)
        f.close()



    def minmax(self,_id_,d,numb):
        a, ex = {}, {}
        minimum, maximum, = {}, {}
        id_minim, id_maxim = 0, 0

        for dis in d:
            if dis['source'][0] == _id_:
                a.update({dis['target'][0]:dis['weight']})
            elif dis['target'][0] == _id_:
                a.update({dis['source'][0]:dis['weight']})

        for i in arange(numb):
            id_minim = min(a, key=a.get)
            minimum.update({id_minim:a[id_minim]})
            ex.update({id_minim:a[id_minim]})
            del a[id_minim]

        a = dict((n, a.get(n, 0)+ex.get(n, 0)) for n in set(a)|set(ex))

        for i in arange(numb):
            id_maxim = max(a, key=a.get)
            maximum.update({id_maxim:a[id_maxim]})
            del a[id_maxim]

        return minimum, maximum


    def write_neighbours(self,_id_,mi,ma,f):
        con = Connection()
        db = con.extraction_test
        s = db.song_test.find()

        for song in s:
            if song['song_id'] == _id_:
                a = ("Source id : " + str(song['song_id']) + " --- Titel: " + song['metadata']['title'] +\
                 " --- Artist: " + song['metadata']['artist'] + " --- Genre: " + song['metadata']['genre']).encode('utf-8')
                f.write(len(a)*"*"+"\n")
                f.write(a+"\n")
                f.write(len(a)*"*"+"\n")
        s.rewind()
        f.write("Minimal distances"+"\n")
        f.write("_________________________"+"\n")
        for son in s:
            for id_ in mi:
                if son['song_id'] == id_:
                    f.write("Distance: " + str(mi[id_]) + "  " + son['metadata']['title'].encode('utf-8') + "\n")
        f.write("_________________________"+"\n")
        s.rewind()
        f.write("Maximal distances"+"\n")
        f.write("_________________________"+"\n")
        for so in s:
            for id_ in ma:
                if so['song_id'] == id_:
                    f.write("Distance: " + str(ma[id_]) + "  " + so['metadata']['title'].encode('utf-8') + "\n")
        f.write("_________________________"+"\n")
        f.write("\n")

