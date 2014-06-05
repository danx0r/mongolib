import __init__ as mng

xyzabc = 1234
def test():
    abc=333
    x=111
    print mng.parseQuery("foo == xyzabc or bat == abc and bar=='xyz'", locals(), globals())
    print "connect:", mng.connect()
    print mng.upsert("test1", "foo == x", locals(), foo=x, bar="xyz")
    print mng.update("test1", "foo == x", locals(), **{'foo': x, 'bar': "xyz"})
    print mng.query("test1").count()
    print mng.parseQuery("foo == x and bar=='xyz'", locals())
    print mng.query("test1", "foo == x and bar=='xyz'", locals(), fields="bar", exclude="_id")[0]
    xyz = {'abc':{'123':'xyz'}}
    print mng.upsert("test1", "+box", box = [{'a':11}, {'a':12, 'b':44}], foo="bar", bar="foo")
    print mng.query("test1", "box[1].a == 12", fields={'$and': [{'box': True}, {'box': {'$slice': [1, 2]}}]})[0]
    print mng.query("test1", "box[1].a == 12", fields="box[-1:], -_id, NO_OTHER_FIELDS")[0]
    print mng._db.test1.count()
    rec = mng.query("test1")[0]
    mng.update("test1", "_id==rec['_id']", locals(), fee="SUCCESS")
    print mng.query("test1", "_id==rec['_id']", locals())[0]['fee']
    print mng.query("test1", "rec['_id']", locals())[0]['fee']
    print mng.upsert("test1", "_id=='barker'")
    print mng.query("test1", "_id==~'bark'")[0]
    print mng.query("test1", "'barker'")[0]
test()
