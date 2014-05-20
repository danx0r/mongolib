from mongolib import *

# class foo(object):
#     pass

xyzabc = 1234
def test():
    abc=333
    x=111
    print pyng.parseQuery("foo == xyzabc or bat == abc and bar=='xyz'", {a:b for a, b in globals().items() + locals().items()})
    print "connect:", connect("127.0.0.1", 27017, "test_mongolib")
    print upsert("test1", "foo == x", locals(), foo=x, bar="xyz")
    print query("test1").count()
    print pyng.parseQuery("foo == x and bar=='xyz'", locals())
    print query("test1", "foo == x and bar=='xyz'", locals(), fields="bar", exclude="_id")[0]
    xyz = {'abc':{'123':'xyz'}}
    print query("test1", "foo.baz==12345 and bar==xyz['abc']['123']", locals(), fields=("bar, -_id"))[0]
    print upsert("test1", "box == [1,2,3]", box=[1,2,3])
    print query("test1", "+box")[0]
    print query("test1", "box == {'$size' : 3}", fields="-_id, box[1:]")[0]

test()