#
# shell for simple mongo ops
# run in ipython for best result
#
import sys, bson, traceback
sys.path.append('../')
from mongolib import *
import mongolib
from datetime import datetime
from datetime import timedelta

def _prompt_drop_collection(*args, **kw):
    print "drop", args, kw
    print "are you sure? (type 'yes' to proceed):"
    if raw_input()[:3] == 'yes':
        print "ok, here goes"
        _real_drop_collection(*args, **kw)
    else:
        print "ok, cancelled"

_real_drop_collection = pymongo.database.Database.drop_collection
pymongo.database.Database.drop_collection = _prompt_drop_collection

def __short_repr__(self):
    return "<BSONBinaryBlob %d bytes>" % len(self)

bson.binary.Binary.__repr__ = __short_repr__

try:
    if len(sys.argv) > 1:
        print "connect:", connect(sys.argv[1])
    else:
        print "connect:", connect()
    _db = mongolib._db
    print "connected to:", _db
    print "available collections:"
    try:
        for c in _db.collection_names(): 
            try:
                print " ", c, _db[c].count(), "items"
            except:
                print "oops, no access!"
    except:
        print "oops, no access!"
except:
    print traceback.format_exc()
    print "USAGE: ipython -i shell.py database_name"
