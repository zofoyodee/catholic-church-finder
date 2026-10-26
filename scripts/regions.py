"""State and province names for the search index, so "Santa Fe NM" and "Santa Fe New Mexico" both work.

Overture gives most regions as their postal or ISO code (NM, ON, NSW, CMX, SP); a few as full names.
Run on its own to add the region column to existing search files without rebuilding everything:
    python3 scripts/regions.py data
"""
import glob, json, os, re, sys

NAMES = {
 'US': dict(AL='Alabama', AK='Alaska', AZ='Arizona', AR='Arkansas', CA='California', CO='Colorado', CT='Connecticut', DE='Delaware',
            DC='District of Columbia Washington', FL='Florida', GA='Georgia', HI='Hawaii', ID='Idaho', IL='Illinois', IN='Indiana', IA='Iowa',
            KS='Kansas', KY='Kentucky', LA='Louisiana', ME='Maine', MD='Maryland', MA='Massachusetts', MI='Michigan', MN='Minnesota',
            MS='Mississippi', MO='Missouri', MT='Montana', NE='Nebraska', NV='Nevada', NH='New Hampshire', NJ='New Jersey', NM='New Mexico',
            NY='New York', NC='North Carolina', ND='North Dakota', OH='Ohio', OK='Oklahoma', OR='Oregon', PA='Pennsylvania', RI='Rhode Island',
            SC='South Carolina', SD='South Dakota', TN='Tennessee', TX='Texas', UT='Utah', VT='Vermont', VA='Virginia', WA='Washington',
            WV='West Virginia', WI='Wisconsin', WY='Wyoming', PR='Puerto Rico', GU='Guam', VI='Virgin Islands'),
 'CA': dict(AB='Alberta', BC='British Columbia', MB='Manitoba', NB='New Brunswick', NL='Newfoundland and Labrador', NS='Nova Scotia',
            NT='Northwest Territories', NU='Nunavut', ON='Ontario', PE='Prince Edward Island', QC='Quebec', SK='Saskatchewan', YT='Yukon'),
 'AU': dict(ACT='Australian Capital Territory', NSW='New South Wales', NT='Northern Territory', QLD='Queensland', SA='South Australia',
            TAS='Tasmania', VIC='Victoria', WA='Western Australia'),
 'MX': dict(AGU='Aguascalientes', BCN='Baja California', BCS='Baja California Sur', CAM='Campeche', CHP='Chiapas', CHH='Chihuahua',
            CMX='Ciudad de Mexico CDMX Mexico City', COA='Coahuila', COL='Colima', DUR='Durango', GUA='Guanajuato', GRO='Guerrero',
            HID='Hidalgo', JAL='Jalisco', MEX='Estado de Mexico', MIC='Michoacan', MOR='Morelos', NAY='Nayarit', NLE='Nuevo Leon',
            OAX='Oaxaca', PUE='Puebla', QUE='Queretaro', ROO='Quintana Roo', SLP='San Luis Potosi', SIN='Sinaloa', SON='Sonora',
            TAB='Tabasco', TAM='Tamaulipas', TLA='Tlaxcala', VER='Veracruz', YUC='Yucatan', ZAC='Zacatecas'),
 'BR': dict(AC='Acre', AL='Alagoas', AP='Amapa', AM='Amazonas', BA='Bahia', CE='Ceara', DF='Distrito Federal', ES='Espirito Santo',
            GO='Goias', MA='Maranhao', MT='Mato Grosso', MS='Mato Grosso do Sul', MG='Minas Gerais', PA='Para', PB='Paraiba', PR='Parana',
            PE='Pernambuco', PI='Piaui', RJ='Rio de Janeiro', RN='Rio Grande do Norte', RS='Rio Grande do Sul', RO='Rondonia', RR='Roraima',
            SC='Santa Catarina', SP='Sao Paulo', SE='Sergipe', TO='Tocantins'),
}
CODES = {cc: {v.split(' ')[0].lower(): k for k, v in t.items()} for cc, t in NAMES.items()}

def region_label(cc, region):
    """'NM New Mexico' for a coded region, the region itself when it is a name, '' for numbers."""
    r = (region or '').strip()
    if not r or re.fullmatch(r'[\d\W]+', r): return ''
    t = NAMES.get(cc)
    if t:
        if r.upper() in t: return f'{r.upper()} {t[r.upper()]}'
        for k, v in t.items():  # a full name: add its code
            if v.lower().startswith(r.lower()) or r.lower() == v.split(' ')[0].lower(): return f'{k} {v}'
    return r

def search_line(name, town, cc, region):
    return f"{name}\t{town}\t{cc}\t{region_label(cc, region)}".replace('\n', ' ')

def write_chunks(out_dir, search, limit=4_500_000):
    chunks = []; cur = []; size = 0
    for s in search:
        b = len(s.encode()) + 1
        if size + b > limit: chunks.append(cur); cur = []; size = 0
        cur.append(s); size += b
    chunks.append(cur)
    for old in glob.glob(f'{out_dir}/search-*.txt'): os.remove(old)
    for ci, c in enumerate(chunks):
        with open(f'{out_dir}/search-{ci}.txt', 'w') as f: f.write('\n'.join(c))
    return chunks

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'data'
    meta = json.load(open(f'{out}/meta.json'))
    search = []
    for k in range(meta['shards']):
        for r in json.load(open(f'{out}/d/{k}.json')): search.append(search_line(r[0], r[2], r[5], r[3]))
    chunks = write_chunks(out, search)
    meta['searchChunks'] = len(chunks); meta['searchSizes'] = [len(c) for c in chunks]
    json.dump(meta, open(f'{out}/meta.json', 'w'))
    print(len(search), 'rows in', len(chunks), 'chunks')
