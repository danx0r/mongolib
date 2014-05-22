#
# shell for simple mongo ops
# run in ipython for best result
#
import sys
sys.path.append('../')
from mongolib import *
import mongolib

if len(sys.argv) < 2:
    print "USAGE: ipython -i shell.py database_name"
    exit()
else:
    connect(sys.argv[1])
    _db = mongolib._db
    print "available collections:"
    for c in _db.collection_names(): 
        print " ", c, _db[c].count(), "items"