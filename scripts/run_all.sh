cd /tmp/claude-0/ov
proc(){ k=$1; i=$(echo $k | grep -oE 'part-[0-9]+' ); [ -f $i.jsonl ] && return; [ "$i" = part-00000 ] && cp p0.jsonl $i.jsonl && return
  curl -s --retry 4 -o $i.parquet "https://overturemaps-us-west-2.s3.amazonaws.com/$k" && python3 -I /tmp/claude-0/scripts/extract.py $i.parquet $i.jsonl.tmp && mv $i.jsonl.tmp $i.jsonl; rm -f $i.parquet; }
export -f proc
cat keys.txt | xargs -P 3 -I{} bash -c 'proc {}'
echo ALLDONE
