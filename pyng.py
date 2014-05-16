"""

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions 
    of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
    TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
    CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
    DEALINGS IN THE SOFTWARE.

pyng is a pythonic persistence layer and _query syntax

first version implemented using mongodb

import pyng

db = pyng.coll("db1")
db.append(foo="bat", bar=1.0)
db.append({'foo': "bat", 'bar': 2.0})
db['key0'] = {'foo': "bum", 'bar': 3.14159}
x = db('foo') == "bat" or db('bar') > 1.0                #call() operator creates a _query object for key string, with overloaded operators
#x = db.missing('barf')
#x = db.exists('foo')
#x = db.regex('foo', "^bat.$")
#x = db.reNoCase('foo', "bat")
x[0]                                        #first call to mongo for _query?
> {'foo': "bat", 'bar': 2.0}
x[0] |= {'bass': "heavy"}
x[0]
> {'foo': "bat", 'bar': 2.0, 'bass': "heavy"}
x[0].bar
> 2.0
x[0]['bar'] = {}
x[0].bar.sam = 1
x[0].bar.al = 2
x[0].bar.bob = 3
x[0].bar
> {'sam': 1, 'al': 2, 'bob': 3}
x[0].bar.bob += 1
x[0].lst = []
x[0].lst.append(456)
x[0].lst.append(789)
x = db.len('lst') >= 2
print x
[{'foo': "bat", 'bar': {'sam': 1, 'al': 2, 'bob': 4}, 'bass': "heavy", 'lst': [456, 789]}]
x[0].lst[1]
789
"""

import pymongo, sys, traceback, re, time, datetime
# from pprint import pprint
from pp_json import pp_json as pprint
# from copy import deepcopy
#
# _query objects overload operators, build up a parsed _query tree. You'll see.
#
class _query(object):
    def __init__(self, key, coll=None, op=None):
        self.key = key
        self.coll = coll
        if self.coll:
            self.q = self.coll.colname + ':' + key
        else:
            self.q = key
        if op:
            self.q = {op: self.q}

    def __eq__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
#         print "eq called:", self, cmp
        self.q = {'eq':[self.q, cmp.q]}
#         print "--->", self
        return self
        
    def __gt__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
#         print "gt called:", self, cmp
        self.q = {'gt':[self.q, cmp.q]}
#         print "--->", self
        return self
        
    def __lt__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
        self.q = {'lt':[self.q, cmp.q]}
        return self
        
    def __ge__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
        self.q = {'ge':[self.q, cmp.q]}
        return self
        
    def __le__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
        self.q = {'le':[self.q, cmp.q]}
        return self
        
    def __ne__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
        self.q = {'ne':[self.q, cmp.q]}
        return self
        
    def __or__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
#         print "or called:", self, cmp
        self.q = {'or':[self.q, cmp.q]}
#         print "--->", self
        return self
    
    def __and__(self, cmp):
        if type(cmp) != type(self):
            cmp = _query(cmp)
#         print "and called:", self, cmp
        self.q = {'and':[self.q, cmp.q]}
#         print "--->", self
        return self
    
    def __getitem__(self, key):
        return "<item at index %s from %s>" % (key, self)

    def get(self):
        m = _qtree2mongo(self.q)
        return self.coll.mongo_collection.find(m)

    def __repr__(self):
        return "<_query:%s%s>" % (self.coll.colname + ':' if self.coll else "", self.q)

class collection(object):
    def __init__(self, dbname=None, colname=None, host="127.0.0.1", port=27017, user=None, password=None):
        if dbname:
            self.dbname = dbname
            self.colname = colname
            try:
                self.client = pymongo.MongoClient(host, port)
                if user:
                    self.client[dbname].authenticate(user, pw)
                self.mongo_collection = self.client[dbname][colname]
                print "connection successful to collection:", self.colname, self.mongo_collection
            except:
                print >> sys.stderr, traceback.format_exc()
    #
    # coll('foo') returns a _query object wrapper around 'foo'
    #
    def __getitem__(self, key):
        return _query(key, self)

    def __getattr__(self, key):
#         print "getattr", args, kw
        return _query(key, self)

    def exists(self, key):
        return _query(key, self, 'exists')

    def missing(self, key):
        return _query(key, self, 'missing')

    def test(self):
        print "test method -- will __getattr__ override?"

"""
convert our logical, clean, rational parse tree to MDB's kludge-bucket of a cluster of hacks
example:
{'gt': ['db.foo', 1.0]}
-->
{'foo': {'$gt': 1.0}}

{'or': [{'gt': ['db:foo', 1.1]}, {'eq': ['db:bar', 2]}]}
-->
{'$or': [{'foo': {'$gt': 1.1}}, {'bar': 2}]}
"""

BINARY_OPS = {'le':'$lte', 'ge':'$gte', 'eq':None, 'ne':'$ne', 'lt':'$lt', 'gt':'$gt'}
LOGIC_OPS = {'and':'$and', 'or':'$or'}
UNARY_OPS = {'exists':'$exists', 'missing':'$exists'}

def _strip_prefix(s):
    try:
        if ':' in s:
            s = s[s.find(':')+1:]
    except:
        pass
    return s

def _qtree2mongo(q):
    key = q.keys()[0]
    if key in BINARY_OPS or key in LOGIC_OPS:
        ab = list(q[key])           #should be a 2-element list for binary ops
        for i in range(len(ab)):
#             print "DEBUG", ab[i], type(ab[i]),type(ab[i]) == dict 
            if type(ab[i]) == dict:
                ab[i] = _qtree2mongo(ab[i])
#                 print "                                               A", i, ab[i]
            else:
                ab[i] = _strip_prefix(ab[i])
#                 print "                                               B", i, ab[i]
        if key in BINARY_OPS:
            op = BINARY_OPS[key]
            a, b = ab
            if op:
                m = {a: {op: b}}
            else:
                m = {a: b}                 #special case for ==
        else:
            op = LOGIC_OPS[key]
            m = {op: ab}            #TODO: consolidate for >2 elements in list

    elif key in UNARY_OPS:
        op = UNARY_OPS[key]
        m = {_strip_prefix(q[key]): {op: True if key=='exists' else False}}     #yuck, I've been slimed
    else:
        print >> sys.stderr, "error parsing ops in _qtree2mongo"
        exit()
    return m


if __name__ == "__main__":
    db = collection('test', 'test')
#     q = (db.foo == 1.1) & ( (db.foo2 > db['test']) | db.exists('foo3') )              #db['test'] avoids conflict with db.test()
    q = (db.foo == 'bar') & (db.missing('zeba'))
    print "result:", q
    pprint(q.q)
    print q[0]
    m =  _qtree2mongo(q.q)
    print "mongo query:", m
    pprint(m)
    print "mongo find:"
    rows = q.get()
    pprint(list(rows))
#
# pony style:
#
    def select(*args, **kw):
        print args, kw
    Db = (1,2,3)
    select(q for q in Db if q.foo == 1.1 and q.foo2 > q['test'] or q.exists('foo3'))
