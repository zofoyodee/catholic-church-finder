# usage: rangecat.py URL START END  -> writes a valid PBF (file header blob + all data blobs whose start is in [START,END)) to stdout
import sys, subprocess, struct
url, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
out = sys.stdout.buffer
def curl(a, b=None):
    rng = f'{a}-{b}' if b is not None else f'{a}-'
    return subprocess.Popen(['curl','-sS','--retry','5','-r',rng,url], stdout=subprocess.PIPE, bufsize=1<<20).stdout
def varint(b, i):
    r=s=0
    while True:
        c=b[i]; i+=1; r|=(c&0x7f)<<s; s+=7
        if c<0x80: return r,i
def hdr_size(h):
    i=0; ds=None; t=None
    while i<len(h):
        key,i=varint(h,i); f,w=key>>3,key&7
        if w==2:
            l,i=varint(h,i); v=h[i:i+l]; i+=l
            if f==1: t=v
        elif w==0:
            v,i=varint(h,i)
            if f==3: ds=v
        else: raise ValueError
    return t, ds
# file header blob
f=curl(0, 65535); b=f.read(65536)
hl=struct.unpack('>I',b[:4])[0]; t,ds=hdr_size(b[4:4+hl]); assert t==b'OSMHeader'
if start==0:
    pos=0
else:
    out.write(b[:4+hl+ds])
    # resync near start
    g=curl(start, start+70*1024*1024); w=g.read(); pos=None; k=0
    while True:
        p=w.find(b'\x0a\x07OSMData', k); assert p>=4
        L=struct.unpack('>I',w[p-4:p])[0]
        try:
            tt,dd=hdr_size(w[p:p+L])
            q=p+L+dd
            if tt==b'OSMData' and w[q+4:q+4+9]==b'\x0a\x07OSMData': pos=start+p-4; break
        except Exception: pass
        k=p+1
SIZE=95631115419
s=curl(pos)
cur=pos
def rd(n):
    global s
    buf=b''
    while len(buf)<n:
        d=s.read(n-len(buf))
        if not d: raise EOFError
        buf+=d
    return buf
while cur < end and cur < SIZE:
    try:
        l4=rd(4); L=struct.unpack('>I',l4)[0]; h=rd(L); tt,dd=hdr_size(h); body=rd(dd)
    except EOFError:
        if cur >= SIZE: break
        sys.stderr.write(f'resume at {cur}\n'); s=curl(cur); continue
    out.write(l4); out.write(h); out.write(body); cur+=4+L+dd
out.flush()
