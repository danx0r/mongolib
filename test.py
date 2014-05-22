# from mongolib import *
import mongolib as mng

xyzabc = 1234
def test():
    abc=333
    x=111
    print mng.parseQuery("foo == xyzabc or bat == abc and bar=='xyz'", locals(), globals())
    print "connect:", mng.connect("test_mongolib")
    print mng.upsert("test1", "foo == x", locals(), foo=x, bar="xyz")
    print mng.update("test1", "foo == x", locals(), **{'foo': x, 'bar': "xyz"})
    print mng.query("test1").count()
    print mng.parseQuery("foo == x and bar=='xyz'", locals())
    print mng.query("test1", "foo == x and bar=='xyz'", locals(), fields="bar", exclude="_id")[0]
    xyz = {'abc':{'123':'xyz'}}
    print mng.query("test1", "foo.baz==12345 and bar==xyz['abc']['123']", locals(), fields=("bar, -_id"))[0]
    print mng.upsert("test1", "+box", box = [{'a':11}, {'a':12, 'b':44}], foo="bar", bar="foo")
    print mng.query("test1", "box[1].a == 12", fields={'$and': [{'box': True}, {'box': {'$slice': [1, 2]}}]})[0]
    print mng.query("test1", "box[1].a == 12", fields="box[-1:], -_id, NO_OTHER_FIELDS")[0]
    print mng._db.test1.count()

test()