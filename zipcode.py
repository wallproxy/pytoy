#!/usr/bin/env python
"""
:license: MIT

Copyright (C) 2012 HustMoon

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import with_statement

import zlib, sys

def b128encode(buf, escape=False):
    if not buf: return ''
    buf = bytearray(buf)
    res = bytearray((len(buf) * 8 + 6) / 7)
    p, s, i = 0, 1, 0
    for n in buf:
        res[i] = ((p << (8 - s) | (n >> s)) & 0x7F) | 0x80; i += 1
        if s == 7:
            res[i] = n | 0x80; i += 1
            p, s = 0, 1
        else:
            p, s = n, (s + 1) % 8
    if s != 1:
        if s == 2 and p < 0x80:
            i -= 1
        else:
            p = (p << (8 - s)) & 0x7F
        p = chr(p)
        if escape:
            p = p.encode('string-escape')
        res[i:] = p
    return str(res)

def dcode():
    code = r'''def code(__=code):
 (_______)=(globals)();del((_______)['code'])
 if(((_______).get('__doc__'))is((None))):
  (__)=(map)((ord),(__)[(339):]);(______)=[0]*(((((len)((__))+(1))*(7))/(8)));((___),(____),(_____))=((0),(0),(0))
  for((__))in((__)):
   if((__)<(128)):break
   if((____)==(0)):((___),(____))=((__),(1))
   else:
    (______)[(_____)]=((((___)<<(____))|(((__)&(127))>>((7)-(____))))&(255));(_____)+=(1);((___),(____))=((__),(((____)+(1))%(8)))
  if((__)<(128)):
   if((____)!=(0)):
    (__)=((((___)<<(____))|((__)>>((7)-(____))))&(255))
   (______)[(_____):]=[((__))]
  elif((____)!=(0)):del((______)[(_____):])
  exec((''.join((map)((chr),(______))).decode('zlib')))in((_______))
  if(((_______).get('__doc__'))is((None))):(_______)['__doc__']=''
code()
'''
    return ''.join([c.encode('string-escape') if ord(c) < 128 else c
                    for c in zlib.compress(code, 9)])
dcode = dcode()

def encode(infile, outfile):
    with open(infile, 'rU') as fp:
        code = fp.read().rstrip('\n') + '\n'
    code = b128encode(zlib.compress(code, 9), True)
    code = r'''# -*- coding: latin-1 -*-
code = '%s'
exec(code.decode('zlib'))
''' % (dcode + code)
    with open(outfile, 'wb') as fp:
        fp.write(code)

def decode(infile, outfile):
    with open(infile, 'rU') as fp:
        code = fp.read().rstrip('\n') + '\n'
    code = code.replace("exec(code.decode('zlib'))", "exec(code.decode('zlib')"
        ".replace('exec','fp.write').replace('in((_______))',''))")
    with open(outfile, 'wb') as fp:
        eval(compile(code, 's', 'exec'), {'fp':fp})

def main():
    try:
        if sys.argv[1] == '-d':
            func = decode
            infile, outfile = sys.argv[2:4]
        else:
            func = encode
            infile, outfile = sys.argv[1:3]
    except (IndexError, ValueError):
        print >>sys.stderr, 'Usage: zipcode.py [-d] infile.py outfile.py'
        raise SystemExit(-1)
    func(infile, outfile)

if __name__ == '__main__':
    main()
