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

mongolib is a simple layer of convenience routines to help with everyday tasks using mongodb in python.

The underlying principle is to provide the most pythonic, simplified, easy-to-write, easy-to-read syntax possible.
"""

import pymongo, sys, traceback, re


RECONNECT_TRIES = 10
RECONNECT_WAIT = 30

def connect(host, port, db, user=None, pw=None):
    global _db, _dbname, _host, _port, _user, _pw
    _host = host
    _port = port
    _dbname = db
    _user = user
    _pw = pw
    try:
        _client = pymongo.MongoClient(host, port)
        if user:
            _client.test.authenticate(user, pw)
        _db = _client[db]
        return True
    except:
        return traceback.format_exc()

def _query(collection, *filter, **kw):
#     print "args:", filter
#     print "keywords:", kw
    db = _db[collection]
    limit = kw['limit'] if 'limit' in kw else None
    fields = kw['fields'] if 'fields' in kw else ()
    exclude = kw['exclude'] if 'exclude' in kw else ()
    desc = kw['desc'] if 'desc' in kw else None
    asc = kw['asc'] if 'asc' in kw else None
    if len(filter) and type(filter[0]) == dict:
        q = filter[0]
    else:
        q = _parse_args(filter)
    f = {}
    if type(fields) in (list, tuple, dict):
        fields = list(fields)
    else:
        fields = [fields]
    for field in fields:
        f[field] = True

    if type(exclude) in (list, tuple, dict):
        fields = list(exclude)
    else:
        fields = [exclude]
    for field in fields:
        f[field] = False

#     print "query:", q
#     print "fields:", f
    if len(f):
        cur = db.find(q, f)
    else:
        cur = db.find(q)
    if limit:
        cur = cur.limit(limit)
    if desc:
        cur = cur.sort([(desc, -1)])
    if asc:
        cur = cur.sort([(asc, 1)])
    return cur

def query(*args, **kw):
    try:
        return _query(*args, **kw)
    except:
        exc = traceback.format_exc()
        if not ("pymongo.errors" in exc and "not valid at server" in exc):
            print >> sys.stderr, exc
            raise Exception("mongolib quit")
        for i in range(RECONNECT_TRIES):
            print >> sys.stderr, "WARNING mongolib.query connection lost, attempting reconnect try %d" % i, args, kw
            err = connect(_host, _port, _dbname, _user, _pw)
            if err == True:
                return _query(*args, **kw)
            print >> sys.stderr, err
            time.sleep(RECONNECT_WAIT)
        print >> sys.stderr, "ERROR mongolib.query could not reconnect, exiting"
        raise Exception("mongolib quit")

#
# args are filter, keywords are update
#
# update(db.table, "ass =", 4, bar=14, _UPSERT_=True, _MULTI_=True)
#
def _update(collection, *filter, **kw):
#     print "args:", filter
#     print "kw:", kw
    db = _db[collection]
    q = {}
    if len(filter) and type(filter[0]) == dict:
        q = filter[0]
    else:
        q = _parse_args(filter)
    multi = upsert = False
    if '_UPSERT_' in kw:
        del kw['_UPSERT_']
        upsert = True
    if '_MULTI_' in kw:
        del kw['_MULTI_']
        multi = True
    if "_UPDATE_" in kw:
        up = kw['_UPDATE_']
    else:
        for key in kw:
            if "__" in key:
                val = kw[key]
                del kw[key]
                kw[key.replace("__", '.')] = val
        if kw == {}:
            kw = dict(q)
            if '_id' in q:
                q = {'_id': kw['_id']}
                del kw['_id']
        up = {'$set': kw}
#     print "query:", q
#     print "update:", up
    if q == {}:
        return db.insert(kw)
    else:
        ret = db.update(q, up, upsert = upsert, multi = multi)
#     print ret, type(ret)
    if ret['err']:
        pass
    elif ret['updatedExisting']:
        ret = ret['n']
    else:
        if 'upserted' in ret:
            ret = ret['upserted']
        else:
            if ret['n'] == 1:
                ret = "new"
            else:
                ret = ret['n']
    return ret

def update(*args, **kw):
    try:
        return _update(*args, **kw)
    except:
        exc = traceback.format_exc()
        if not ("pymongo.errors" in exc and "not valid at server" in exc):
            print >> sys.stderr, exc
            raise Exception("mongolib quit")
        for i in range(RECONNECT_TRIES):
            print >> sys.stderr, "WARNING mongolib.update connection lost, attempting reconnect try %d" % i, args, kw
            err = connect(_host, _port, _dbname, _user, _pw)
            if err == True:
                return _update(*args, **kw)
            print >> sys.stderr, err
            time.sleep(RECONNECT_WAIT)
        print >> sys.stderr, "ERROR mongolib.update could not reconnect, exiting"
        raise Exception("mongolib quit")

def upmulti(*args, **kw):
    kw['_MULTI_'] = True
    return update(*args, **kw)

def upsert(*args, **kw):
    kw['_UPSERT_'] = True
    return update(*args, **kw)

def uppush(*args, **kw):
    for key in kw:
        if "__" in key:
            val = kw[key]
            del kw[key]
            kw[key.replace("__", '.')] = val
    return update(*args, _UPDATE_={'$push': kw})

def insert(db, rec):
    return upsert(db, {}, **rec)

_op_table = {
    "<": "$lt",
    ">": "$gt",
    "<=": "$lte",
    ">=": "$gte",
    "!=": "$ne",
}

_split_chars = "<>=!~ "

def _split_exp(exp):
    exp = exp.strip()
    splt = []
    for i in range(len(exp)):
        if exp[i] in _split_chars:
            splt.append(exp[:i].strip())
            break
    if len(splt) > 0:
        for j in range(i, len(exp)):
            if exp[j] not in _split_chars:
                if len(exp[i:j].strip()):
                    splt.append(exp[i:j].strip())
                break
        if len(splt) > 1:
            splt.append(exp[j:].strip())
        else:
            splt.append(exp[i:].strip())
    else:
        splt.append(exp)
    return splt

def andify(a, k, b):
    ands = []
    for key, val in a.items():
        ands.append({key: val})
    ands.append({k: b})
    return {'$and': tuple(ands)}

def _parse_arg(arg):
    try:
        return int(arg)
    except:
        try:
            return float(arg)
        except:
            return arg

def _parse_args(args):
    if type(args) != list:
        args = list(args)
    q = {}
    while len(args):
        arg = args.pop(0)
        filt_op = _split_exp(arg)
        if len(filt_op) == 1:
            q[filt_op[0]] = {'$exists': True}
        else:
            filt, op = filt_op[:2]
            if op == "not":
                if filt in q:
                    q = andify(q, filt, {'$exists': False})
                else:
                    q[filt] = {'$exists': False}
            else:
                if len(filt_op) == 3:
                    arg2 = _parse_arg(filt_op[2])
                else:
                    arg2 = args.pop(0)
                if op == "==":
                    if filt in q:
                        q = andify(q, filt, arg2)
                    else:
                        q[filt] = arg2
                elif op == "~=":
                    arg2 = re.compile(arg2)
                    if filt in q:
                        q = andify(q, filt, arg2)
                    else:
                        q[filt] = arg2
                elif op == "~~":
                    arg2 = re.compile(arg2, re.IGNORECASE)
                    if filt in q:
                        q = andify(q, filt, arg2)
                    else:
                        q[filt] = arg2
                elif op in _op_table:
                    if filt in q:
                        q = andify(q, filt, {_op_table[op]: arg2})
                    else:
                        q[filt] = {_op_table[op]: arg2}
                else:
                    raise Exception("ERROR: unknown operation in _parse_args: %s" % op)
    return q

if __name__ == "__main__":   
    from pprint import pprint
    print "connect:", connect("127.0.0.1", 27017, "test_mongolib")
    print query("test1").count()
    print upsert("test1", "foo == 12345", foo=12345, bar="bat")
    print query("test1").count()
    print query("test1", "foo==12345", "bar==bat")[0]
