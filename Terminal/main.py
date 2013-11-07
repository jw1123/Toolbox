#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conversion import Conversion
from extraction import Extraction
from distance import Distance



#ffmpeg
#aubio
#bregman
#pymongo
#mutagen


if __name__ == "__main__":

    print "This is a script to help extract audio features and to calculate distances between songs with choice parameters."
    print "All data is stored in a database of MongoDB."
    print "The script only works with wave files, being named in a way described later. You can give mp3 or m4a files (ID3 taged!) "
    print "to the script and it will convert them towave files with ffmpeg for you. Make sure ffmpeg and mutagen are installed."
    print "For audio feature extraction, this script is using the bregman audio toolbox and aubio toolbox (for the rhythm) "
    print "which you have to download and install (make sure both work)."
    print "There is also a set of prerequisits for python: you should have installed numpy, etc." #update all python packages that have to be installed
    print "__________________________________________"
    print "At any time, press q if you want to quit."
    print "__________________________________________"

    y = None

    while (y != "q"):
        message = "What do you want to do? File conversion (c), feature extraction (e) or distance calculation(d)? : "
        y = raw_input(message)

        if y == "c":
            c = Conversion()
        elif y == "e":
            e = Extraction()
        elif y == "d":
            d = Distance()
        elif y == "q":
            print "Goodbye!"
        else:
            print "There is no %r option, please try again." %(y)
