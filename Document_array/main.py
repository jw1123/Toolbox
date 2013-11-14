#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conversion import Conversion
from extraction import Extraction
from distance import Distance
from neighbour import Neighbour
from sys import argv
from timeit import timeit
from getopt import getopt


if __name__ == "__main__":

    options, rem = getopt(argv[1:], 'c:e:d:n:h', ['conversion=','extraction=','distance','neighbour','help'])
    
    
    for opt,arg in options:
        if opt in ('-c','--conversion'):
            c = Conversion(arg,rem[0])
        elif opt in ('-e','--extraction'):
            e = Extraction(arg,rem[0])
        elif opt in ('-d','--distance'):
            d = Distance()
        elif opt in ('-n','--neighbour'):
    	    n = Neighbour()
        elif opt in ('-h','--help'):
            print """The following options are available:
            -c, --conversion                                          : conversion of m4a and mp3 files to wave files
            -e, --extraction (with either 'new' or 'add' as argument) : feature extraction of either a new set or adding features to a set
            -d, --distance                                            : calculate the distance between each song
            -n, --neighbour                                           : creates a file with every song and its three nearest and farest neighbours
            NOTE: If you use conversion or extraction, you have to add the path to the file with your m4a/mp3 files or wave files respectively
            EXAMPLE: python main.py -e new /Users/myname/Document/wave/
            """

#print timeit("Distance()", setup="from distance import Distance", number=2)