Simple syntax for mongo query & update. Sits on pymongo


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

    connect("database_name")
    (will use config.py if found for defaults

The db is remembered for subsequent calls. comparisons include typical operators,
plus ==~ for (case insensitive) regex

    query("test", "foo ==~ 'bar'")
    #will return all docs where 'bar' is in foo, with any case

Other methods include upsert, upmulti, insert
