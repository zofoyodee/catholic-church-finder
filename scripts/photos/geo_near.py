# Stream a geo_tags dump, keep page ids within R metres of a church. Output: page_id lat lon church_idx dist
import sys, gzip, re, numpy as np
from scipy.spatial import cKDTree
dump, out, R = sys.argv[1], sys.argv[2], float(sys.argv[3])
c = np.load('/tmp/claude-0/work/churches.npz')
def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]
tree = cKDTree(xyz(c['lat'], c['lon']))
rx = re.compile(rb"\(\d+,(\d+),'earth',(\d),(-?[\d.]+),(-?[\d.]+),")
buf_id=[]; buf_lat=[]; buf_lon=[]; n=0
fo = open(out, 'w')
def flush():
    global buf_id, buf_lat, buf_lon
    if not buf_id: return
    d, i = tree.query(xyz(np.array(buf_lat), np.array(buf_lon)), distance_upper_bound=R/6371000)
    for k in np.nonzero(np.isfinite(d))[0]:
        fo.write(f"{buf_id[k]}\t{buf_lat[k]}\t{buf_lon[k]}\t{i[k]}\t{d[k]*6371000:.0f}\n")
    buf_id=[]; buf_lat=[]; buf_lon=[]
with gzip.open(dump, 'rb') as f:
    for line in f:
        for m in rx.finditer(line):
            buf_id.append(int(m.group(1))); buf_lat.append(float(m.group(3))); buf_lon.append(float(m.group(4))); n+=1
        if len(buf_id) > 500000: flush()
flush(); print('rows', n)
