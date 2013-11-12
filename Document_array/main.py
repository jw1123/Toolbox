#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conversion import Conversion
from extraction import Extraction
from distance import Distance
from neighbour import Neighbour
from sys import argv


if __name__ == "__main__":
    
    y = argv[1]
    

    if y == "-cmp3" or y == "-cm4a":
        c = Conversion(y)
    elif y == "-enew" or y == "-eadd":
        e = Extraction(y)
    elif y == "-d":
        d = Distance()
    elif y == "-n":
    	n = Neighbour()
    else:
        print "There is no %r option. Try -cmp3 -cm4a -enew -eadd -d or -n." %(y)
