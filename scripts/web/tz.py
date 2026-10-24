"""Time zone of a church from its country and position (good enough for "Mass soon")."""
ONE = dict(IT='Europe/Rome', FR='Europe/Paris', ES='Europe/Madrid', PH='Asia/Manila', PL='Europe/Warsaw', DE='Europe/Berlin',
           CO='America/Bogota', AR='America/Argentina/Buenos_Aires', GB='Europe/London', VN='Asia/Ho_Chi_Minh', IN='Asia/Kolkata',
           PT='Europe/Lisbon', AT='Europe/Vienna', PE='America/Lima', CL='America/Santiago', KR='Asia/Seoul', EC='America/Guayaquil',
           NG='Africa/Lagos', BE='Europe/Brussels', PY='America/Asuncion', JP='Asia/Tokyo', PR='America/Puerto_Rico', GT='America/Guatemala',
           IE='Europe/Dublin', ZA='Africa/Johannesburg', CR='America/Costa_Rica', CH='Europe/Zurich', VE='America/Caracas',
           SV='America/El_Salvador', TW='Asia/Taipei', NL='Europe/Amsterdam', HU='Europe/Budapest', RO='Europe/Bucharest',
           DO='America/Santo_Domingo', NI='America/Managua', CZ='Europe/Prague', KE='Africa/Nairobi', BO='America/La_Paz',
           MY='Asia/Kuala_Lumpur', LK='Asia/Colombo', HN='America/Tegucigalpa', HR='Europe/Zagreb', TH='Asia/Bangkok',
           SK='Europe/Bratislava', CI='Africa/Abidjan', UY='America/Montevideo', PA='America/Panama', SI='Europe/Ljubljana',
           LT='Europe/Vilnius', LV='Europe/Riga', UA='Europe/Kyiv', CM='Africa/Douala', GH='Africa/Accra', TZ='Africa/Dar_es_Salaam',
           UG='Africa/Kampala', LB='Asia/Beirut', MT='Europe/Malta', CU='America/Havana', NZ='Pacific/Auckland', SG='Asia/Singapore',
           HK='Asia/Hong_Kong', MO='Asia/Macau', CN='Asia/Shanghai', LU='Europe/Luxembourg', DK='Europe/Copenhagen', SE='Europe/Stockholm',
           NO='Europe/Oslo', FI='Europe/Helsinki', GR='Europe/Athens', IL='Asia/Jerusalem', PS='Asia/Hebron', JO='Asia/Amman',
           SY='Asia/Damascus', IQ='Asia/Baghdad', EG='Africa/Cairo', RW='Africa/Kigali', BI='Africa/Bujumbura', ZM='Africa/Lusaka',
           ZW='Africa/Harare', MW='Africa/Blantyre', MZ='Africa/Maputo', AO='Africa/Luanda', MG='Indian/Antananarivo', ET='Africa/Addis_Ababa',
           SN='Africa/Dakar', BJ='Africa/Porto-Novo', TG='Africa/Lome', BF='Africa/Ouagadougou', GA='Africa/Libreville', CG='Africa/Brazzaville',
           BA='Europe/Sarajevo', RS='Europe/Belgrade', AL='Europe/Tirane', MK='Europe/Skopje', BY='Europe/Minsk', BG='Europe/Sofia',
           EE='Europe/Tallinn', IS='Atlantic/Reykjavik', JM='America/Jamaica', TT='America/Port_of_Spain', HT='America/Port-au-Prince',
           BZ='America/Belize', GY='America/Guyana', SR='America/Paramaribo', PG='Pacific/Port_Moresby', TL='Asia/Dili', PK='Asia/Karachi',
           BD='Asia/Dhaka', MM='Asia/Yangon', KH='Asia/Phnom_Penh', LA='Asia/Vientiane', AE='Asia/Dubai', KW='Asia/Kuwait', QA='Asia/Qatar',
           BH='Asia/Bahrain', SA='Asia/Riyadh', OM='Asia/Muscat', GU='Pacific/Guam', MP='Pacific/Saipan', FJ='Pacific/Fiji', WS='Pacific/Apia',
           MU='Indian/Mauritius', RE='Indian/Reunion', GP='America/Guadeloupe', MQ='America/Martinique', GF='America/Cayenne',
           AD='Europe/Andorra', MC='Europe/Monaco', SM='Europe/San_Marino', VA='Europe/Vatican', LI='Europe/Vaduz', CY='Asia/Nicosia',
           GE='Asia/Tbilisi', AM='Asia/Yerevan', TR='Europe/Istanbul', SS='Africa/Juba', SD='Africa/Khartoum', NA='Africa/Windhoek',
           BW='Africa/Gaborone', LS='Africa/Maseru', SZ='Africa/Mbabane', LR='Africa/Monrovia', SL='Africa/Freetown', GN='Africa/Conakry',
           ML='Africa/Bamako', NE='Africa/Niamey', TD='Africa/Ndjamena', CF='Africa/Bangui', ER='Africa/Asmara', DJ='Africa/Djibouti',
           SC='Indian/Mahe', CV='Atlantic/Cape_Verde', GQ='Africa/Malabo', ST='Africa/Sao_Tome', BS='America/Nassau', BB='America/Barbados',
           LC='America/St_Lucia', GD='America/Grenada', VC='America/St_Vincent', DM='America/Dominica', AG='America/Antigua',
           KN='America/St_Kitts', AW='America/Aruba', CW='America/Curacao', VI='America/St_Thomas', BM='Atlantic/Bermuda')


def tz_of(cc, lon, lat):
    if cc in ONE:
        return ONE[cc]
    if cc == 'US':
        if lon < -154 and lat < 23: return 'Pacific/Honolulu'
        if lon < -130: return 'America/Anchorage'
        if lat < 37 and -115 < lon < -109: return 'America/Phoenix'
        return 'America/New_York' if lon > -86.5 else 'America/Chicago' if lon > -101 else 'America/Denver' if lon > -114.5 else 'America/Los_Angeles'
    if cc == 'CA':
        if lon > -60 and lat > 46.5 and lon < -52: return 'America/St_Johns'
        return 'America/Halifax' if lon > -67 else 'America/Toronto' if lon > -90 else 'America/Winnipeg' if lon > -102 else 'America/Edmonton' if lon > -120 else 'America/Vancouver'
    if cc == 'BR':
        return 'America/Sao_Paulo' if lon > -52 else 'America/Manaus' if lon > -67.5 else 'America/Rio_Branco'
    if cc == 'MX':
        return 'America/Tijuana' if lon < -114.5 else 'America/Mazatlan' if lon < -105.5 else 'America/Cancun' if lon > -89.5 else 'America/Mexico_City'
    if cc == 'AU':
        if lon < 129: return 'Australia/Perth'
        if lon < 138 and lat > -26: return 'Australia/Darwin'
        if lon < 141: return 'Australia/Adelaide'
        return 'Australia/Brisbane' if lat > -28.5 else 'Australia/Hobart' if lat < -39.5 else 'Australia/Sydney'
    if cc == 'ID':
        return 'Asia/Jakarta' if lon < 114.5 else 'Asia/Makassar' if lon < 127 else 'Asia/Jayapura'
    if cc == 'CD':
        return 'Africa/Kinshasa' if lon < 22 else 'Africa/Lubumbashi'
    if cc == 'RU':
        return 'Europe/Kaliningrad' if lon < 23 else 'Europe/Moscow' if lon < 50 else 'Asia/Yekaterinburg' if lon < 70 else 'Asia/Novosibirsk' if lon < 95 else 'Asia/Irkutsk' if lon < 115 else 'Asia/Vladivostok'
    if cc == 'KZ':
        return 'Asia/Almaty' if lon > 60 else 'Asia/Aqtobe'
    # elsewhere: a whole-hour offset from longitude (Etc/GMT signs are reversed)
    h = round(lon / 15)
    return 'UTC' if h == 0 else f'Etc/GMT{"-" if h > 0 else "+"}{abs(h)}'
