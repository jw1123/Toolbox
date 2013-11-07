#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from mutagen.id3 import ID3
from subprocess import call, STDOUT, PIPE

class Conversion():

    def __init__(self):

        x, y = None, None
        self.first, self.second = [], []

        print "CONVERSION"
        print "You chose to convert audio files. There are three steps to complete the conversion."
        print "First: If you have m4a files, they must be converted to mp3 files. So create a M4A"
        print "folder and put all the m4a files in that folder, plus create an MP3 folder."
        print "Second: Once you only have mp3 files, you have to add their ID3 tags to them."
        print "You can do this through iTunes or any other way you want. Save the files again in a"
        print "folder named MP3TAG."
        print "Third: Create a folder named WAVE for the output files."

        print "If you have m4a files, type in first the directory to the M4A folder and then the directory to the MP3 folder."
        print "Else type in skip (s): "

        i = 0
        while x != 's' or i < 2:
            x = raw_input("Directory: ")
            if x != 's':
                self.first.append(x)
            i+=1
        if len(self.first) == 2:
            self.m4a_to_mp3(self.first[0],self.first[1])
        print "Now add the ID3 tags. Once you've done it, create a folder MP3TAG and save all"
        print "the tagged mp3 files in it. Create a WAVE folder."
        print "Type in first the directory to the MP3TAG folder and then the directory to the WAVE folder: "

        j = 0
        while j < 2:
            y = raw_input("Directory: ")
            self.second.append(y)
            j+=1
        if len(self.second) == 2:
            self.mp3_to_wave(self.second[0],self.second[1])



    def m4a_to_mp3(self,inp,out):
        for root,dirs,files in walk(inp):
            for fil in files:
                if fil[len(fil)-3:len(fil)] == "m4a":
                    try:
                        call(["ffmpeg", "-i", inp+fil, out+fil[0:len(fil)-3]+"mp3"])
                    except:
                        print "%r could not be converted." % (fil)
        print "Conversion completed."


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









