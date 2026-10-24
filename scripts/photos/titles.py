# Stream page.sql from stdin; print page_id, namespace, title for ids in props.json.
import sys, re, json
ids = {int(k) for k in json.load(open(sys.argv[1]))}
rx = re.compile(rb"^\((\d+),(\d+),'((?:[^'\\]|\\.)*)',")
fo = open(sys.argv[2], 'w'); n = 0
for line in sys.stdin.buffer:
    if line[:1] != b'(': continue
    m = rx.match(line)
    if m and int(m.group(1)) in ids:
        fo.write(f"{m.group(1).decode()}\t{m.group(2).decode()}\t{m.group(3).decode('utf-8','replace')}\n"); n += 1
print('found', n)
