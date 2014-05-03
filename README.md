Simple syntax for mongo query & update.


 mongolib is a simple layer of convenience routines to help with everyday tasks using mongodb in python.

 The underlying principle is to provide the most pythonic, simplified, easy-to-write, easy-to-read syntax possible.

 examples:

    PyMongo> db.test.update({'foo': 'bar'}, {'$set': {'foo': 'baz'}})

 becomes:

    mongolib> update("test", "foo==bar", foo='baz')

and

    PyMongo> db.test.find({'foo': 'bar'}, fields={'foo':True, 'ban':True})

 becomes:

    mongolib> query("test", "foo==bar", fields=('foo', 'ban'))


you connect using:

    connect(host, port, db, user=None, pw=None)

The db is remembered for subsequent calls.

Methods include upsert, upmulti
