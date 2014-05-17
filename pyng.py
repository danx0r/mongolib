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

import compiler
from compiler.ast import *

LOGICAL_OPS = {And: 'and', Or: 'or'}

def _parseAst(ast):
    q = ast
    if ast.__class__ in LOGICAL_OPS:
        print "DEBUG logical and/or"
#         q =  
#     print ast.getChildren()
    return ast
    
def parse(exp):
    p = compiler.parse(exp)
#     print p
    if p.getChildren()[0] == None:
        p = p.getChildren()[1].getChildren()[0]
    else:
#         print "DEBUG", p.getChildren()
        p = Const(p.getChildren()[0])                   #for some reason Python parses a single string as a module ref not const
    if p.__class__==Discard:
        p = p.getChildren()[0]
    q = _parseAst(p)
    return q

if __name__ == "__main__":   
    mq = parse("'bus'")
    print mq