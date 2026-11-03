cd "$(dirname "$0")"
U=https://osm-pds.s3.amazonaws.com/planet-latest.osm.pbf; SZ=95631115419; N=6
for k in ${PARTS:-$(seq 0 $((N-1)))}; do
  a=$((SZ*k/N)); b=$((SZ*(k+1)/N))
  ( python3 -I rangecat.py $U $a $b | osmium tags-filter -R -F pbf - \
 'nwr/denomination=roman_catholic,catholic,greek_catholic,ukrainian_greek_catholic,maronite,melkite,syro-malabar,syro_malabar,syro-malankara,syro_malankara,chaldean_catholic,chaldean,armenian_catholic,coptic_catholic,syriac_catholic,ruthenian_catholic,byzantine_catholic,romanian_greek_catholic,slovak_greek_catholic,eastern_catholic,latin_catholic,ethiopian_catholic,eritrean_catholic,hungarian_greek_catholic,ruthenian,italo-albanian,Roman_Catholic,roman catholic' \
 'nwr/amenity=place_of_worship' 'nwr/building=church,chapel,cathedral' -o A$k.osm.pbf --overwrite; echo part $k done $? ) &
done
wait; echo ALLDONE
