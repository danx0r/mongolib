#
# pretty-print a JSON type dict/list:
#
import urllib
from datetime import datetime
def is_atomic(x):
#     return type(x) in (str, unicode, int, float, bool, datetime, type(None))
    return type(x) not in (dict, list)    

def is_stringy(x):
    return type(x) in (str, unicode)

INDENT = 4
def pp_json_dict(d, indent):
    if len(d) == 0:
        print "{}"
        return
    print " " * indent + "{"
    keys = d.keys()
    keys.sort()
    for key in keys:
        print " " * (indent+INDENT) + "'" + key + "':",
        val = d[key]
        if is_atomic(val):
            pp_json_atom(val)
        else:
            if len(val):
                print
            pp_json(val, indent+INDENT)
    print " " * indent + "},"

def pp_json_list(d, indent):
    if len(d) == 0:
        print "[]"
        return
    print " " * indent + "["
    for key in range(len(d)):
        val = d[key]
        if is_atomic(val):
            print (" " * (indent+INDENT))[:-1],
            pp_json_atom(val)
        else:
            pp_json(val, indent+INDENT)
    print " " * indent + "],"

def pp_json_atom(val):
    if type(val) in (int, long, float, str, unicode, bool, datetime, type(None)):
        s = ""
        if is_stringy(val):
            if val.find("http://") == 0:
#                 print "DEBUG url decode raw:", type(val), val
                val = urllib.unquote(unicode(val)).encode('latin-1')         #wtf is up with dat
            if '"' in val:
                val = "'"+val+"'"
            else:
                val = '"'+val+'"'
            s += " " + val + ","
        else:
            s += " " + str(val) + ","
        try:
            print s
        except:
            print s.encode('utf-8')
    else:
        if "bson.objectid" in str(type(val)):
            print val
        else:
            print type(val),
            try:
                print len(val), "bytes"
            except:
                print
    
def pp_json(j, indent=0):
    if type(j) == dict:
        pp_json_dict(j, indent)
    elif type(j) == list:
        pp_json_list(j, indent)
    else:
#         pp_json_atom(j)
        print "ERROR pp_json: not atom but not dict or list:", type(j), len(j), "bytes"

if __name__ == "__main__":
    u = u'\u8349\u67f3\u8bba\u575b\u5730\u5740'
    x = {'u':u,'zzz':123456, 'aaa':"simple strings"}
    x['zz-top'] = {'subdict:': u'\u575b\u5730'}
    x['listless'] = [1,2,3]
    x['bad_ascii'] = u'\xa0'
    pp_json(x)
