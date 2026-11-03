cd "$(dirname "$0")"
U=https://osm-pds.s3.amazonaws.com/planet-latest.osm.pbf; SZ=95631115419; N=6
for k in ${PARTS:-$(seq 0 $((N-1)))}; do
  a=$((SZ*k/N)); b=$((SZ*(k+1)/N))
  ( python3 -I rangecat.py $U $a $b 2>>resume.log | osmium getid -F pbf - -i idsB$k.txt -o B$k.osm.pbf --overwrite 2>B$k.err; echo part $k done $? ) &
done
wait; echo ALLDONE
