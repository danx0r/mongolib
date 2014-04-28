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
"""

import  subprocess, time, os, sys

MAXLINES=100

def run(*args, **kw):
    if 'timeout' in kw:
        timeout = float(kw['timeout'])
        print "running", args[0], "with timeout:", timeout,
        del kw['timeout']
    else:
        timeout = 0
    if 'showoutput' in kw:
        showoutput = kw['showoutput']
        print "showoutput:", showoutput
        del kw['showoutput']
    else:
        showoutput = False
    try:
        if not timeout:
            kw['stderr'] = subprocess.STDOUT
            out = subprocess.check_output(*args, **kw)
            err = ""
        else:
            proc = subprocess.Popen(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            t0 = time.time()
            out = ""
            err = ""
            complete = False
            while time.time() < t0 + timeout:
                line = proc.stdout.readline()
                out += line
                line = proc.stderr.readline()
                err += line
                i = 0
                while line != "":
                    if showoutput:
                        sys.stdout.write(line)
                    i += 1
                    if i >= MAXLINES:
                        break
                    line = proc.stdout.readline()
                    out += line
                    line = proc.stderr.readline()
                    err += line
                if proc.poll() != None:
                    complete = True
                    #get all output
                    line = proc.stdout.readline()
                    out += line
                    while line != "":
                        if showoutput:
                            sys.stdout.write(line)
                        sys.stdout.write(line)
                        line = proc.stdout.readline()
                        out += line
                        line = proc.stderr.readline()
                        err += line
                    sys.stdout.flush()
                    break
##                sys.stdout.write(".")
##                sys.stdout.flush()
                time.sleep(0.2)
            if not complete:
                proc.kill()

    except subprocess.CalledProcessError as e:
        out = e.output
    return out, err, complete

if __name__ == "__main__":
    print "test run.py"
    cmd = "ls", "-rltR", "/home/dbm/"
    s, err = run(cmd, timeout=2, showoutput=True)
    print "output----------\n", s
    print "end output------"
    print "completed:", err
