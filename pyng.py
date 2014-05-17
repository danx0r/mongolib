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
def _parseAst(ast, position=0):
    q = ast
    if ast.__class__ == Const:
        if position == 0:
            raise Exception("ERROR -- no const on left side")
#         print "DEBUG Const", ast.getChildren()
        q = ast.getChildren()[0]
    elif ast.__class__ == Name:
#         print "DEBUG Name", ast.getChildren()
        q = ast.getChildren()[0]
        if position > 0:                                #convert to Python object in present namespace (avoid eval like the plague it is!)
            try:
                q = locals()[q]
            except:
                q = globals()[q]
    elif ast.__class__ == Compare:
        a, op, b = ast.getChildren()
        op = COMPARE_OPS[op]
        a = _parseAst(a, 0)
        b = _parseAst(b, 1)
#         print "DEBUG cmp", a, op, b
        if op:
            q = {a: {op: b}}
        else:
            q = {a: b}                                  #special eq case
    elif ast.__class__ == Getattr:
#         print "DEBUG dot", ast.getChildren()
        a, b = ast.getChildren()
        a = _parseAst(a, position)
        b = _parseAst(b, position)
        q = a + "." + b
    elif ast.__class__ == Invert:                       #~ means regex!
        a = ast.getChildren()[0]
        a = _parseAst(a, 1)
#         print "DEBUG regex", a
        q = re.compile(a, re.IGNORECASE)
    elif ast.__class__ in LOGICAL_OPS:
#         print "DEBUG logical and/or"
        args = []
        for x in ast.getChildren():                        #should always be 2 children
            args.append(_parseAst(x))
        q = {LOGICAL_OPS[ast.__class__]: args}
    return q
    
def parse(exp):
    p = compiler.parse(exp)
#     print p
    if p.getChildren()[0] == None:
        p = p.getChildren()[1].getChildren()[0]
    else:
        p = Const(p.getChildren()[0])                   #for some reason Python parses a single string as a module ref not const
    if p.__class__==Discard:
        p = p.getChildren()[0]
    q = _parseAst(p)
    return q

if __name__ == "__main__":
    foo = 444
    bus = "BUSS"
#     mq = parse("foo == 'bar' or foo < bus.fzz.bat")        #need better error checks for right side .syntax
    mq = parse("foo ==~ 'bar' or bus.fzz.bat != bus")
#     print type(mq)
    print mq
