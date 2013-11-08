#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conversion import Conversion
from extraction import Extraction
from distance import Distance
from sys import argv


if __name__ == "__main__":
    
    y = argv[1]
    

    if "-c" in y:
        c = Conversion(y)
    elif "-e" in y:
        e = Extraction(y)
    elif y == "-d":
        d = Distance()
    else:
        print "There is no %r option. Try -cmp3 -cm4a -e or -d." %(y)
