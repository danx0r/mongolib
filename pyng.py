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

reworking pyng as pythonic query generator for mongo

parse("foo == 'bar' or bus > 4")
> {'$or', [{'foo': 'bar'}, {'bus': {'$gt': 4}}]}

simplistic use:
db.test.find(parse("foo == 'bar' or bus > 4")

use directly in mongolib:
update("foo == 'bar' or bus > 4", fields=('foo', 'bar', 'bus'))
"""

import compiler, sys, re
from compiler.ast import *

LOGICAL_OPS = {And: '$and', Or: '$or'}
BINARY_OPS = {And: '$and', Or: '$or'}
COMPARE_OPS = {'==': None, '<': '$lt', '>': '$gt', '<=': '$lte', '>=': '$gte', '!=': '$ne'}
def _parseQuery(ast, position=0):
#     print "DEBUG parseQuery ast:", ast, "pos:", position
    q = ast
    if type(q) in (str, unicode):
        return q
    if ast.__class__ == Const:
        if position == 0:
            raise Exception("ERROR -- no const on left side")
#         print "DEBUG Const", ast.getChildren()
        q = ast.getChildren()[0]
    elif ast.__class__ == Name:
#         print "DEBUG Name", position, ast.getChildren()
        q = ast.getChildren()[0]
        if position > 0:                                #convert to Python object in present namespace (avoid eval like the plague it is!)
            q = _get_value(q)
#             try:
#                 q = locals()[q]
#             except:
#                 q = globals()[q]
    elif ast.__class__ == Compare:
        a, op, b = ast.getChildren()
        op = COMPARE_OPS[op]
        a = _parseQuery(a, 0)
        b = _parseQuery(b, 1)
#         print "DEBUG cmp", a, op, b
        if op:
            q = {a: {op: b}}
        else:
            q = {a: b}                                  #special eq case
    elif ast.__class__ == Getattr:
#         print "DEBUG dot", ast.getChildren()
        a, b = ast.getChildren()
        a = _parseQuery(a, position)
        b = _parseQuery(b, position)
        try:
            q = a + "." + b
        except:
            q = getattr(a, b)
    elif ast.__class__ == Invert:                       #~ means regex!
        a = ast.getChildren()[0]
        a = _parseQuery(a, 1)
#         print "DEBUG regex", a
        q = re.compile(a, re.IGNORECASE)
    elif ast.__class__ == UnaryAdd:                       #+ means $exists
        a = ast.getChildren()[0]
#         print "DEBUG +", a
        a = _parseQuery(a, 0)
        q = {a: {'$exists': True}}
    elif ast.__class__ == UnarySub:                       #- minus -- missing
        a = ast.getChildren()[0]
#         print "DEBUG +", a
        a = _parseQuery(a, 0)
        q = {a: {'$exists': False}}
    elif ast.__class__ == Subscript:
#         print "DEBUG subscript", ast.getChildren()
        a, b, b = ast.getChildren()
        a = _parseQuery(a, position)
        b = _parseQuery(b, position)
        q = a[b]
    elif ast.__class__ in LOGICAL_OPS:
#         print "DEBUG logical and/or"
        args = []
        for x in ast.getChildren():                        #should always be 2 children
            args.append(_parseQuery(x))
        q = {LOGICAL_OPS[ast.__class__]: args}
    else:
        raise Exception("ERROR in parseQuery -- unknown ast op: %s" % ast.__class__)
    return q
    
def parseQuery(exp):
    p = compiler.parse(exp)
#     print p
    if p.getChildren()[0] == None:
        p = p.getChildren()[1].getChildren()[0]
    else:
        p = Const(p.getChildren()[0])                   #for some reason Python parses a single string as a module ref not const
    if p.__class__==Discard:
        p = p.getChildren()[0]
    q = _parseQuery(p)
    if type(q) != dict:
        raise Exception("Error in parseQuery: didn't parse properly. +foo to test for exists")
    return q

def _parseSelect(ast):
#     print "DEBUG parseSelect ast:", ast
    q = ast
    if ast.__class__ == Name:
#         print "DEBUG Name", ast.getChildren()
        q = {ast.getChildren()[0]: True}
    elif ast.__class__ == Getattr:
#         print "DEBUG dot", ast.getChildren()
        a, b = ast.getChildren()
        a = a.getChildren()[0]                          #should be a Name
        q = {a + "." + b: True}
    elif ast.__class__ == UnarySub:                       #- minus -- missing
        a = ast.getChildren()[0]
        a = _parseSelect(a)
#         print "DEBUG -", a
        if type(a) == dict:
            a = a.keys()[0]
        q = {a: False}
    elif ast.__class__ == Slice:
        a, b, b, c = ast.getChildren()
        a = _parseSelect(a)
        if type(a) == dict:
            a = a.keys()[0]
        if b.__class__ == UnarySub:
            b = -b.getChildren()[0].getChildren()[0]
        else:
            if b:
                b = b.getChildren()[0]                          #should be a Const
            else:
                b = 0
        if c.__class__ == UnarySub:
            c = -c.getChildren()[0].getChildren()[0]
        else:
            if c:
                c = c.getChildren()[0]                          #should be a Const
            else:
                c = 0                                       #None means [1:] syntax
#         print "DEBUG []", a, b, c
        q = {a: {'$slice': [b, c-b]}}
    elif ast.__class__ == Subscript:
        raise Exception("ERROR in parseSelect: subscripts not supported. Use slice notation instead. foo[-1:] returns last element (as list of one)")
    elif ast.__class__ == Tuple:
        q = {}
        for e in ast.getChildren():
            a = _parseSelect(e)
            q.update(a)
    else:
        raise Exception("ERROR in parseSelect: unknown ast op: %s" % ast.__class__)
#     print "  --> parseSelect returns:", q
    return q
    
def parseSelect(exp):
    p = compiler.parse(exp)
#     print p
    if p.getChildren()[0] == None:
        p = p.getChildren()[1].getChildren()[0]
    else:
        p = Const(p.getChildren()[0])                   #for some reason Python parses a single string as a module ref not const
    if p.__class__==Discard:
        p = p.getChildren()[0]
    q = _parseSelect(p)
    return q

if __name__ == "__main__":
    foo = 444
    bus = "BUSS"
    class fuzz(object):
        pass
    bat = fuzz()
    bat.bar = 456
    dik = {}
    dik['dat'] = 789
    
#     mq = parse("foo == 'bar' or foo < bus.fzz.bat")        #need better error checks for right side .syntax
    mq = parseQuery("-foo or x!=bat.bar")
    print mq
    mq = parseQuery("bar > 4 and foo == dik['dat']")
    print mq
    ms = parseSelect("bat.fff[-1:], -bar.fzz")
    print ms

#
# O ye innocents, avert thine eyes
#
import inspect

def _get_value(name):
    frame = inspect.stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[name]
