#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import walk
from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from subprocess import call, STDOUT, PIPE


class Conversion():

    def __init__(self, path):

        print "CONVERSION"

        #____________________________________________________
        input_path = path  # Change the input path # ###REPLACE####
        call(["mkdir", path + "wave/"])
        output_path = path + "wave/"  # Change the output path # ###REPLACE###
        #____________________________________________________

        self.any_to_wave(input_path, output_path)

    def any_to_wave(self, inp, out):
        for root, dirs, files in walk(inp):
            for fil in files:
                end = fil[len(fil)-3:len(fil)]
                if end in ["mp3","mp4","mp4"]:
                    if end == "mp3":
                        tag = ID3(inp + fil)
                    elif end == "mp4" or end == "m4a":
                        mp4 = MP4(inp + fil)
                        tag = mp4.MP4Tags

                    if "TIT2" in tag:
                        titel = str(tag["TIT2"])
                    else:
                        titel = ''
                    if "TPE1" in tag:
                        artist = str(tag["TIT2"])
                    else:
                        artist = ''
                    if "TALB" in tag:
                        album = str(tag["TALB"])
                    else:
                        album = ''
                    if "TCON" in tag:
                        genre = str(tag["TCON"])
                    else:
                        genre = ''
                    if "TDRC" in tag:
                        year = str(tag["TDRC"])
                    else:
                        year = ''
                    call(["ffmpeg", "-i", inp + fil, "-ar", "11000",
                        out + titel
                        + "-*-" + artist
                        + "-*-" + album
                        + "-*-" + genre
                        + "-*-" + year
                        + ".wav"],
                        stderr=STDOUT, stdout=PIPE)



        print "Conversion successfully completed!"
