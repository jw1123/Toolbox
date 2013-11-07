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
    elif y == "-e":
        e = Extraction()
    elif y == "-d":
        d = Distance()
    else:
        print "There is no %r option, please try again." %(y)
