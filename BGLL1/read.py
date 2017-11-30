# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 12:20:29 2017

@author: zcl
"""

lines_seen = set() 
outfile = open("allr2.txt","w")
for line in open("all2.txt","r"):
    if line not in lines_seen:
        outfile.write(line)
        lines_seen.add(line)
outfile.close()