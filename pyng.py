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

pyng is a pythonic persistence layer and query syntax

first version implemented using mongodb

import pyng

db = pyng.obj("db1")
db.append(foo="bat", bar=1.0)
db.append({'foo': "bat", 'bar': 2.0})
db['key0'] = {'foo': "bum", 'bar': 3.14159}
x = db('foo') == "bat" or db('bar') > 1.0                #call() operator creates a query object for key string, with overloaded operators
#x = db.missing('barf')
#x = db.exists('foo')
#x = db.regex('foo', "^bat.$")
#x = db.reNoCase('foo', "bat")
x[0]                                        #first call to mongo for query?
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
from pprint import pprint
# from copy import deepcopy
#
# query objects overload operators, build up a parsed query tree. You'll see.
#
class query(object):
    def __init__(self, key, obj):
        self.key = key
        self.q = key
        self.obj = obj

    def __eq__(self, cmp):
        if type(cmp) != type(self):
            cmp = query(cmp, self.obj)
        print "eq called:", self, cmp
        self.q = {'eq':[self.q, cmp.q]}
        print "--->", self
        return self
        
    def __gt__(self, cmp):
        if type(cmp) != type(self):
            cmp = query(cmp, self.obj)
        print "gt called:", self, cmp
        self.q = {'gt':[self.q, cmp.q]}
        print "--->", self
        return self
        
    def __or__(self, cmp):
        if type(cmp) != type(self):
            cmp = query(cmp, self.obj)
        print "or called:", self, cmp
        self.q = {'or':[self.q, cmp.q]}
        print "--->", self
        return self
        
    def __repr__(self):
        return "<query:%s:%s>" % (self.obj.name, self.q)

class obj(object):
    def __init__(self, name=None, host="127.0.0.1", port=27017, user=None, password=None):
        if name:
            self.name = name
    #
    # obj('foo') returns a query object wrapper around 'foo'
    #
    def __call__(self, key):
        return query(key, self)


if __name__ == "__main__":
    db = obj('db')
#     foo = db('foo')
#     foo2 = db('foo2')
#     foo3 = db('foo3')
    q = (db('foo') == "foo2") | (db('foo2') > "foo3")
    print "result:", q
    