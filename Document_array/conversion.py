#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from mutagen.id3 import ID3
from subprocess import call, STDOUT, PIPE


class Conversion():

    def __init__(self, a, path):

        print "CONVERSION"

        #____________________________________________________
        input_path = path  # Change the input path # ###REPLACE####
        call(["mkdir", path + "wave/"])
        output_path = path + "wave/"  # Change the output path # ###REPLACE###
        #____________________________________________________

        if a == "mp3":
            self.mp3_to_wave(input_path, output_path)
        elif a == "m4a":
            self.m4a_to_mp3(input_path, output_path)

    def m4a_to_mp3(self, inp, out):
        for root, dirs, files in walk(inp):
            for fil in files:
                if fil[len(fil)-3:len(fil)] == "m4a":
                    try:
                        call(["ffmpeg", "-i", inp + fil,
                            out+fil[0:len(fil)-3] + "mp3"])
                    except:
                        print "%r could not be converted." % (fil)
        print "Conversion successfully completed!"

    def mp3_to_wave(self, inp, out):
        for root, dirs, files in walk(inp):
            for fil in files:
                if fil[len(fil)-3:len(fil)] == "mp3":
                    a = 0
                    tag = ID3(inp + fil)
                    # Testing if there is a year-tag, to avoid error due to
                    # incorrect key value
                    try:
                        b = tag["TDRC"]
                        a = 1
                    except:
                        a = 0
                    # MP3 files are converted to WAVE files by invoking
                    # ffmpeg in the terminal
                    # As file name, ID3 tags are used in the following way:
                    # Title -*- Artist -*- Album -*- Genre (-*- Year)
                    try:
                        if a == 1:
                            call(["ffmpeg", "-i", inp + fil, "-ar", "11000",
                                out + str(tag["TIT2"])
                                + "-*-" + str(tag["TPE1"])
                                + "-*-" + str(tag["TALB"])
                                + "-*-" + str(tag["TCON"])
                                + "-*-" + str(tag["TDRC"])
                                + ".wav"],
                                stderr=STDOUT, stdout=PIPE)
                        else:
                            call(["ffmpeg", "-i", inp + fil, "-ar", "11000",
                                out + str(tag["TIT2"])
                                + "-*-" + str(tag["TPE1"])
                                + "-*-" + str(tag["TALB"])
                                + "-*-" + str(tag["TCON"])
                                + ".wav"],
                                stderr=STDOUT, stdout=PIPE)
                    except:
                        print "%r could not be converted" % (fil)
        print "Conversion successfully completed!"
