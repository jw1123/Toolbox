#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from mutagen.id3 import ID3
from subprocess import call, STDOUT, PIPE

class Conversion():

    def __init__(self,a):

        print "CONVERSION"

        input_path = "/Users/jonathan/Documents/DesktopiMac/"
        output_path = "/Users/jonathan/Documents/DesktopiMac"

        if a == "-cmp3":
            self.mp3_to_wave(input_path,output_path)
        elif a == "-cm4a":
            self.m4a_to_mp3(input_path,output_path)


    def m4a_to_mp3(self,inp,out):
        for root,dirs,files in walk(inp):
            for fil in files:
                if fil[len(fil)-3:len(fil)] == "m4a":
                    try:
                        call(["ffmpeg", "-i", inp+fil, out+fil[0:len(fil)-3]+"mp3"])
                    except:
                        print "%r could not be converted." % (fil)
        print "Conversion successfully completed!"


    def mp3_to_wave(self,inp,out):
        for root,dirs,files in walk(inp):
            for fil in files:
                if fil[len(fil)-3:len(fil)] == "mp3":
                    a = 0
                    tag = ID3(inp+fil)
                    try:
                        b = tag["TDRC"]
                        a = 1
                    except:
                        a = 0
                    try:
                        if a == 1:
                            call(["ffmpeg", "-i", inp+fil, "-ar", "11000", out+str(tag["TIT2"])+"-*-"+str(tag["TPE1"])\
                                +"-*-"+str(tag["TALB"])+"-*-"+str(tag["TCON"])+"-*-"+str(tag["TDRC"])+".wav"],\
                                stderr=STDOUT, stdout=PIPE)
                        else:
                            call(["ffmpeg", "-i", inp+fil, "-ar", "11000", out+str(tag["TIT2"])+"-*-"+str(tag["TPE1"])\
                                +"-*-"+str(tag["TALB"])+"-*-"+str(tag["TCON"])+".wav"],\
                                stderr=STDOUT, stdout=PIPE)
                    except:
                        print "%r could not be converted" % (fil)
        print "Conversion successfully completed!"









