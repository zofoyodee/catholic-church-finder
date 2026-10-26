/* Guided tours, church of the day, the liturgical season, and a richer globe
   (stars, atmosphere, day and night, satellite imagery, density glow, golden cathedrals).
   Runs beside the main page script and talks to it through window.ccf. */
(() => {
'use strict';
const ccf = window.ccf;
if (!ccf) return;
const { map, state, esc, reduceMotion } = ccf;
const $ = (id) => document.getElementById(id);
const phone = () => innerWidth <= 640;
const compact = () => matchMedia('(max-width: 640px), (max-height: 500px) and (orientation: landscape)').matches;  // phones either way up (app/mobile.js)
const rad = Math.PI / 180;
const X = '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>';
// page language: the main script's tr() with its English fallback
const i18n = window.ccfI18n;
const T = (k, v) => i18n ? i18n.tr(k, v) : k;
const loc = () => (i18n && i18n.locale) || 'en';
const td = (s) => i18n && i18n.td ? i18n.td(s) : s;

/* ---------- settings kept in this browser ---------- */
const VIEW_KEY = 'ccf-view';
const view = { satellite: false, daynight: true, sky: true, density: true, liturgical: true };
try { Object.assign(view, JSON.parse(localStorage.getItem(VIEW_KEY) || '{}')); } catch (e) {}
const saveView = () => { try { localStorage.setItem(VIEW_KEY, JSON.stringify(view)); } catch (e) {} };

/* ---------- the liturgical calendar ---------- */
// dates are whole days counted from 1970-01-01, so time zones and daylight saving never shift them
const dayNo = (y, m, d) => Math.floor(Date.UTC(y, m - 1, d) / 864e5);
const dow = (n) => (n + 4) % 7; // 0 = Sunday
const fromNo = (n) => new Date(n * 864e5);
function easter(y) {
  const a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
  return dayNo(y, month, day);
}
const COLORS = {
  green: { lit: '#4fae6c', soft: '#9bd9ad', ink: '#06140a', name: 'green' },
  violet: { lit: '#9a6ad6', soft: '#cfb3f2', ink: '#fff', name: 'violet' },
  rose: { lit: '#e48aa8', soft: '#f6c3d4', ink: '#2a0a14', name: 'rose' },
  white: { lit: '#f1e6c4', soft: '#fff6dc', ink: '#1a1406', name: 'white and gold' },
  red: { lit: '#d9464f', soft: '#f3a0a5', ink: '#fff', name: 'red' },
};
const ORD = ['', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh'];
const nth = (n) => n + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th');
const WEEKDAY = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const LORD_FEASTS = new Set(['02-02', '08-06', '09-14', '11-09']); // feasts that replace a Sunday in Ordinary Time
const redFeast = (title) => /Apostle|martyr|Passion|Cross|Innocents|Evangelist|Lawrence/.test(title) && !/Conversion|Chair|John, Apostle and Evangelist/.test(title);

// The season, its colour, and the name of the day
function liturgicalDay(n, cal) {
  const d = fromNo(n), y = d.getUTCFullYear(), wd = dow(n), md = String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0');
  const E = easter(y);
  const xmas = dayNo(y, 12, 25), advent1 = xmas - (dow(xmas) || 7) - 21, christKing = advent1 - 7;
  const jan6 = dayNo(y, 1, 6), baptism = jan6 + (7 - dow(jan6)); // the Sunday after January 6
  const holyFamily = dow(xmas) === 0 ? dayNo(y, 12, 30) : xmas + (7 - dow(xmas));
  const out = { season: '', color: 'green', title: '', key: null, rank: '', week: 0 };
  const sundayOf = (k) => `${ORD[k] || nth(k)} Sunday`;
  const weekdayOf = (k, season) => `${WEEKDAY[wd]} of the ${ORD[k] || nth(k)} Week ${season}`;
  // the pattern behind a numbered day, so each language can name it its own way (dayTitle)
  const pat = (sun, day, k) => ({ key: wd === 0 && sun ? sun : day, w: k, wd });
  if (n >= advent1 && n < xmas) {
    const k = Math.floor((n - advent1) / 7) + 1;
    Object.assign(out, { season: 'Advent', color: n === advent1 + 14 ? 'rose' : 'violet', week: k, title: wd === 0 ? `${sundayOf(k)} of Advent` : weekdayOf(k, 'of Advent'), pat: pat('litSunAdvent', 'litDayAdvent', k) });
  } else if (n >= xmas || n <= baptism) {
    Object.assign(out, { season: 'Christmas Time', color: 'white', title: 'Christmas Time' });
    if (n === xmas) Object.assign(out, { title: 'The Nativity of the Lord', key: 'christmas', rank: 'S' });
    else if (n === holyFamily) Object.assign(out, { title: 'The Holy Family of Jesus, Mary and Joseph', key: 'holyfamily', rank: 'F' });
    else if (n === baptism) Object.assign(out, { title: 'The Baptism of the Lord', rank: 'F' });
    else if (n > xmas && n < xmas + 8) out.title = 'Within the Octave of Christmas';
  } else if (n < E - 46) {
    const k = Math.floor((n - baptism) / 7) + 1;
    Object.assign(out, { season: 'Ordinary Time', week: k, title: wd === 0 ? `${sundayOf(k)} in Ordinary Time` : weekdayOf(k, 'in Ordinary Time'), pat: pat('litSunOrdinary', 'litDayOrdinary', k) });
  } else if (n < E - 3) {
    const k = Math.floor((n - (E - 42)) / 7) + 1;
    Object.assign(out, { season: 'Lent', color: 'violet', week: Math.max(k, 0) });
    if (n === E - 46) out.title = 'Ash Wednesday';
    else if (n < E - 42) Object.assign(out, { title: `${WEEKDAY[wd]} after Ash Wednesday`, pat: pat(null, 'litAfterAsh', 0) });
    else if (n === E - 7) Object.assign(out, { title: 'Palm Sunday of the Passion of the Lord', color: 'red', season: 'Holy Week' });
    else if (n > E - 7) Object.assign(out, { title: `${WEEKDAY[wd]} of Holy Week`, season: 'Holy Week', pat: pat(null, 'litHolyWeek', 0) });
    else Object.assign(out, { title: wd === 0 ? `${sundayOf(k)} of Lent` : weekdayOf(k, 'of Lent'), pat: pat('litSunLent', 'litDayLent', k) });
    if (n === E - 21) out.color = 'rose';
  } else if (n < E) {
    Object.assign(out, { season: 'Easter Triduum', color: n === E - 2 ? 'red' : n === E - 3 ? 'white' : 'violet',
      title: ['Holy Thursday', 'Good Friday', 'Holy Saturday'][n - (E - 3)], key: n === E - 2 ? 'goodfriday' : null });
  } else if (n <= E + 49) {
    const k = Math.floor((n - E) / 7) + 1;
    Object.assign(out, { season: 'Easter Time', color: 'white', week: k, title: wd === 0 ? `${sundayOf(k)} of Easter` : weekdayOf(k, 'of Easter'), pat: pat('litSunEaster', 'litDayEaster', k) });
    if (n === E) Object.assign(out, { title: 'Easter Sunday of the Resurrection of the Lord', pat: null, key: 'easter', rank: 'S' });
    else if (n < E + 7) Object.assign(out, { title: `${WEEKDAY[wd]} within the Octave of Easter`, pat: pat(null, 'litEasterOctave', 0) });
    else if (n === E + 7) Object.assign(out, { title: 'Second Sunday of Easter (Divine Mercy Sunday)', pat: null, key: 'divinemercy' });
    else if (n === E + 39) Object.assign(out, { title: 'The Ascension of the Lord', pat: null, key: 'ascension', rank: 'S' });
    else if (n === E + 49) Object.assign(out, { title: 'Pentecost Sunday', pat: null, key: 'pentecost', rank: 'S', color: 'red' });
  } else {
    const sun = n - wd, k = 34 - Math.round((christKing - sun) / 7);
    Object.assign(out, { season: 'Ordinary Time', week: k, title: wd === 0 ? `${sundayOf(k)} in Ordinary Time` : weekdayOf(k, 'in Ordinary Time'), pat: pat('litSunOrdinary', 'litDayOrdinary', k) });
    const sol = { [E + 56]: ['The Most Holy Trinity', 'trinity'], [E + 63]: ['The Most Holy Body and Blood of Christ', 'corpus'], [E + 68]: ['The Most Sacred Heart of Jesus', 'sacredheart'], [christKing]: ['Our Lord Jesus Christ, King of the Universe', 'christking'] };
    if (sol[n]) Object.assign(out, { title: sol[n][0], pat: null, key: sol[n][1], rank: 'S', color: 'white' });
    else if (n === E + 69) Object.assign(out, { title: 'The Immaculate Heart of the Blessed Virgin Mary', pat: null, key: 'immaculateheart', rank: 'M' });
  }
  // a saint or feast fixed to this date, unless the day already outranks it
  const fixed = cal && cal.fixed.find(f => f[0] === md);
  const protectedDay = n === E - 46 || (n >= E - 7 && n <= E + 7) || out.rank === 'S' || (wd === 0 && /Advent|Lent|Easter/.test(out.season));
  out.saint = null;
  if (fixed && !protectedDay) {
    const [, rank, title, wiki, churches] = fixed, sunday = wd === 0;
    const outranks = rank === 'S' || (rank === 'F' && (!sunday || LORD_FEASTS.has(md) || out.season === 'Christmas Time')) || (!sunday && (rank === 'M' || rank === 'm'));
    if (outranks) {
      if (rank === 'S' || rank === 'F') Object.assign(out, { title, rank, key: md, pat: null, color: redFeast(title) ? 'red' : title === 'All Souls' ? 'violet' : 'white' });
      Object.assign(out, { saint: { title, rank, wiki, md }, wiki, churches });
    }
  }
  if (!out.churches && out.key && cal && cal.moveable[out.key]) out.churches = cal.moveable[out.key][1];
  if (!out.saint && (out.rank === 'S' || out.rank === 'F')) out.saint = { title: out.title, rank: out.rank, wiki: null, md: out.key };
  out.md = md; out.y = y; out.n = n;
  return out;
}
const RANK_KEY = { S: 'rankS', F: 'rankF', M: 'rankM', m: 'rankm' };
const rankName = (r) => RANK_KEY[r] ? T(RANK_KEY[r]) : '';
// the day's name in the page language: numbered days follow the dictionary's pattern, named ones come from the content file
const dayTitle = (d) => {
  if (!d.pat || !i18n || i18n.lang === 'en') return td(d.title);
  const p = d.pat, day = i18n.date(fromNo(d.n), { weekday: 'long' }, true);
  return T(p.key, { n: p.w, ord: ORD[p.w] || nth(p.w), day }).replace(/^./, c => c.toUpperCase());
};
const SEASON_KEY = { 'Advent': 'seasonAdvent', 'Christmas Time': 'seasonChristmas', 'Ordinary Time': 'seasonOrdinary', 'Lent': 'seasonLent', 'Holy Week': 'seasonHolyWeek', 'Easter Triduum': 'seasonTriduum', 'Easter Time': 'seasonEaster' };
const seasonName = (x) => SEASON_KEY[x] ? T(SEASON_KEY[x]) : x;
const colorName = (c) => T('color_' + (COLORS[c] ? c : 'green'));
function churchOfDay(day, cal) {
  const key = day.saint ? day.saint.md : day.key;
  if (key && cal.featured[key] != null) return { i: cal.featured[key], why: 'feast' };
  const list = day.churches || [];
  if (list.length) return { i: list[day.y % Math.min(list.length, 6)], why: 'named' };
  const r = cal.rotation; const doy = day.n - dayNo(day.y, 1, 1);
  return { i: r[(doy * 7 + day.y) % r.length], why: 'rotation' };
}

/* ---------- season colours on the page ---------- */
let today = null;
function applySeason() {
  const root = document.documentElement.style;
  // the Liturgical Season theme borrows the day's colour for its accents, whether or not the season tint is on
  if (today) { const s = COLORS[today.color] || COLORS.green; root.setProperty('--season', s.lit); root.setProperty('--season-soft', s.soft); }
  if (!view.liturgical || !today) { root.removeProperty('--lit'); root.removeProperty('--lit-soft'); root.removeProperty('--lit-ink'); return; }
  const c = COLORS[today.color] || COLORS.green;
  root.setProperty('--lit', c.lit); root.setProperty('--lit-soft', c.soft); root.setProperty('--lit-ink', c.ink);
}
function seasonPill() {
  let b = $('season');
  if (!b) {
    b = document.createElement('button'); b.id = 'season'; b.className = 'season';
    b.setAttribute('aria-controls', 'today'); b.setAttribute('aria-expanded', 'false');
    // the pill opens the church of the day; the (i) beside it explains the season
    const row = document.createElement('div'); row.className = 'season-row';
    row.innerHTML = '<button class="season-i" id="seasonI" aria-expanded="false" aria-controls="seasonInfo">i</button><div class="season-info" id="seasonInfo" role="tooltip" hidden></div>';
    row.prepend(b);
    document.querySelector('.brand').appendChild(row);
    b.addEventListener('click', () => showToday($('today').hidden));
    const info = $('seasonInfo'), ib = $('seasonI');
    const show = (on) => { info.hidden = !on; ib.setAttribute('aria-expanded', on); };
    ib.addEventListener('click', (e) => { e.stopPropagation(); show(info.hidden); });
    ib.addEventListener('mouseenter', () => show(true));
    row.addEventListener('mouseleave', () => show(false));
    document.addEventListener('click', (e) => { if (!row.contains(e.target)) show(false); });
  }
  const sk = SEASON_KEY[today.season] || 'seasonOrdinary';
  $('seasonI').setAttribute('aria-label', T('seasonInfo'));
  $('seasonInfo').innerHTML = `<b>${esc(seasonName(today.season || 'Ordinary Time'))}</b><p>${esc(T('about_' + sk))}</p>`;
  const label = today.season === 'Ordinary Time' && today.week ? T('ordinaryWeek', { season: seasonName('Ordinary Time'), w: today.week }) : today.season ? seasonName(today.season) : dayTitle(today);
  b.innerHTML = `<i aria-hidden="true"></i><span>${esc(label)}</span>`;
  b.title = T('seasonTip', { title: dayTitle(today), color: colorName(today.color) });
}

/* ---------- church of the day ---------- */
const TODAY_KEY = 'ccf-today-closed';
let cal = null, cotd = null;
function buildTodayCard() {
  const el = document.createElement('aside');
  el.id = 'today'; el.className = 'float-card'; el.hidden = true; el.setAttribute('aria-label', T('todayLabel'));
  document.body.appendChild(el);
  return el;
}
async function fillToday() {
  const el = $('today') || buildTodayCard();
  const d = fromNo(today.n);
  const date = i18n ? i18n.date(d, { weekday: 'long', month: 'long', day: 'numeric' }, true) : d.toLocaleDateString('en', { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' });
  let rec = null; try { rec = await ccf.shardFor(cotd.i); } catch (e) {}
  const name = rec ? rec[0] : T('aChurch');
  const where = rec ? [rec[2], ccf.countryName(rec[5])].filter(Boolean).join(', ') : '';
  const s = today.saint;
  const why = cotd.why === 'feast' && s ? T('whyFeast') : cotd.why === 'named' && s ? T(s.rank === 'S' || s.rank === 'F' ? 'whyNamedFeast' : 'whyNamedSaint') : T('whyFeatured');
  el.innerHTML = `<button class="x" id="todayClose" aria-label="${esc(T('todayClose'))}">${X}</button>
    <div class="kick"><b>${esc(date)}</b> · ${esc(today.season ? seasonName(today.season) : T('todayWord'))}</div>
    <div class="saint"><div class="pic"><div class="ph" aria-hidden="true">✠</div></div>
      <div><h2>${esc(s ? td(s.title) : dayTitle(today))}</h2><div class="rank">${esc(s ? rankName(s.rank) + (s.title !== today.title && today.title && !(s.rank === 'S' || s.rank === 'F') ? ' · ' + dayTitle(today) : '') : '')}</div></div></div>
    <button class="cotd" id="cotdGo"><small>${esc(T('cotd'))} · ${esc(why)}</small><b>${esc(name)}</b><span>${esc(where)}</span></button>
    <div class="row"><button class="btn primary" id="cotdVisit">${esc(T('visitGlobe'))}</button>${s && s.wiki ? `<a href="https://en.wikipedia.org/wiki/${encodeURIComponent(s.wiki.replace(/ /g, '_'))}" target="_blank" rel="noopener">${esc(T('aboutSaint', { name: i18n && i18n.lang !== 'en' ? td(s.title) : s.title.replace(/^The /, 'the ') }))}</a>` : ''}</div>`;
  const go = () => { showToday(false, true); ccf.selectChurch(cotd.i, { fly: true }); };
  $('cotdGo').addEventListener('click', go);
  $('cotdVisit').addEventListener('click', go);
  $('todayClose').addEventListener('click', () => showToday(false));
  if (s && s.wiki) saintPicture(s.wiki);
}
async function saintPicture(title) {
  try {
    const r = await fetch('https://en.wikipedia.org/api/rest_v1/page/summary/' + encodeURIComponent(title.replace(/ /g, '_')));
    if (!r.ok) return; const j = await r.json();
    const src = j.thumbnail && j.thumbnail.source; if (!src || !/upload\.wikimedia\.org/.test(src)) return;
    const box = document.querySelector('#today .pic'); if (!box) return;
    const img = new Image(); img.referrerPolicy = 'no-referrer'; img.alt = j.title || ''; img.src = src;
    await img.decode(); box.replaceChildren(img); img.title = T('imgWiki', { name: j.title || '' });
  } catch (e) {}
}
function showToday(open, keep) {
  const el = $('today'); if (!el) return;
  el.hidden = !open; $('season') && $('season').setAttribute('aria-expanded', open);
  if (!open && !keep) { try { localStorage.setItem(TODAY_KEY, String(today.n)); } catch (e) {} }
}
async function initToday() {
  try { cal = await ccf.getJSON('data/calendar.json'); } catch (e) { cal = null; }
  const now = new Date();
  today = liturgicalDay(dayNo(now.getFullYear(), now.getMonth() + 1, now.getDate()), cal);
  applySeason(); seasonPill();
  if (!cal) return;
  cotd = churchOfDay(today, cal);
  await fillToday();
}
window.ccfLiturgicalDay = (y, m, d) => liturgicalDay(dayNo(y, m, d), cal); // handy for checking the calendar from the console

/* ---------- side controls and panels ---------- */
function ctrlButton(id, title, svg, before) {
  const b = document.createElement('button');
  b.id = id; b.className = 'xtra'; b.title = title; b.setAttribute('aria-label', title); b.innerHTML = svg;
  const ref = $(before); ref.parentNode.insertBefore(b, ref);
  return b;
}
const tourBtn = ctrlButton('tourBtn', T('tours'), '<svg viewBox="0 0 24 24"><circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M8 17.2c4-1 2.5-5.2 6-6.4 1.8-.6 3-1.6 3.4-2.8"/><path d="M5 5.5l2 2M7 5.5l-2 2"/></svg>', 'spin');
const viewBtn = ctrlButton('viewBtn', T('globeView'), '<svg viewBox="0 0 24 24"><path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5"/><path d="M3 16.5l9 4.5 9-4.5"/></svg>', 'spin');
tourBtn.setAttribute('aria-expanded', 'false'); tourBtn.setAttribute('aria-controls', 'tours');
viewBtn.setAttribute('aria-expanded', 'false'); viewBtn.setAttribute('aria-controls', 'viewMenu');

// only one side panel at a time: tours, favorites or near me
function closeOthers(except) {
  if (except !== 'tours') showTours(false);
  if (except !== 'favs' && !$('favs').hidden) $('favClose').click();
  if (except !== 'near' && !$('near').hidden) $('nearClose').click();
}
{
  const watch = new MutationObserver(() => { if (!$('favs').hidden || !$('near').hidden) showTours(false); });
  for (const id of ['favs', 'near']) watch.observe($(id), { attributes: true, attributeFilter: ['hidden'] });
}

/* ---------- guided tours ---------- */
let tours = null;
const tour = { t: null, k: 0, auto: true, timer: 0, t0: 0, dwell: 11000, raf: 0, flying: false, spinWas: false };
const toursEl = document.createElement('aside');
toursEl.id = 'tours'; toursEl.className = 'favs'; toursEl.hidden = true; toursEl.setAttribute('aria-labelledby', 'toursTitle');
toursEl.innerHTML = `<header><h2 id="toursTitle"></h2><button class="x" id="toursClose">${X}</button></header><ul id="tourList"></ul><p class="note" id="toursNote"></p>`;
document.body.appendChild(toursEl);
function showTours(open) {
  if (open) closeOthers('tours');
  toursEl.hidden = !open; tourBtn.setAttribute('aria-expanded', open); tourBtn.setAttribute('aria-pressed', open);
  if (open) loadTours().then(renderTourList).catch(() => { $('tourList').innerHTML = `<p class="empty">${esc(T('toursFailed'))}</p>`; });
}
tourBtn.addEventListener('click', () => showTours(toursEl.hidden));
$('toursClose').addEventListener('click', () => showTours(false));
function loadTours() { if (!tours) tours = ccf.getJSON('data/tours.json').then(j => j.tours).catch(e => { tours = null; throw e; }); return tours; }
async function renderTourList() {
  const list = await loadTours();
  const glyph = { marian: 'M', camino: '✦', basilicas: '✠', cathedrals: '♱' };
  $('tourList').innerHTML = list.map(t => `<li><button class="tour" data-t="${esc(t.id)}" style="--c:${esc(t.color)}"><span class="ic" aria-hidden="true">${glyph[t.id] || '✠'}</span><span><b>${esc(t.title)}</b><small>${esc(t.sub)} · ${esc(T('stops', { n: t.stops.length }))}</small></span></button></li>`).join('');
}
$('tourList').addEventListener('click', (e) => { const b = e.target.closest('button[data-t]'); if (b) startTour(b.dataset.t); });

const tourCard = document.createElement('aside');
tourCard.id = 'tourCard'; tourCard.className = 'float-card'; tourCard.hidden = true; tourCard.setAttribute('aria-live', 'polite'); tourCard.setAttribute('aria-label', T('tourGuide'));
document.body.appendChild(tourCard);

function tourGeo(t) {
  return {
    stops: { type: 'FeatureCollection', features: t.stops.map((s, k) => ({ type: 'Feature', geometry: { type: 'Point', coordinates: [s.lon, s.lat] }, properties: { k, n: String(k + 1) } })) },
    route: { type: 'FeatureCollection', features: t.route ? [{ type: 'Feature', geometry: { type: 'LineString', coordinates: t.stops.map(s => [s.lon, s.lat]) }, properties: {} }] : [] },
  };
}
function tourLayers(t) {
  const g = tourGeo(t);
  if (!map.getSource('tour')) {
    map.addSource('tour', { type: 'geojson', data: g.stops });
    map.addSource('tour-route', { type: 'geojson', data: g.route });
    map.addLayer({ id: 'tour-route-glow', type: 'line', source: 'tour-route', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': t.color, 'line-width': 9, 'line-opacity': 0.18, 'line-blur': 4 } }, 'sel-ring');
    map.addLayer({ id: 'tour-route', type: 'line', source: 'tour-route', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': t.color, 'line-width': 2.5, 'line-dasharray': [2, 1.5], 'line-opacity': 0.9 } }, 'sel-ring');
    map.addLayer({ id: 'tour-stop', type: 'circle', source: 'tour', paint: {
      'circle-color': '#05070d', 'circle-stroke-color': t.color, 'circle-stroke-width': 2,
      'circle-radius': ['case', ['==', ['get', 'k'], -1], 13, 10], 'circle-opacity': 0.92 } }, 'sel-ring');
    map.addLayer({ id: 'tour-num', type: 'symbol', source: 'tour', layout: { 'text-field': ['get', 'n'], 'text-font': ['NotoSansMedium'], 'text-size': 11, 'text-allow-overlap': true, 'text-ignore-placement': true }, paint: { 'text-color': t.color } }, 'sel-ring');
  } else {
    map.getSource('tour').setData(g.stops); map.getSource('tour-route').setData(g.route);
    for (const id of ['tour-route-glow', 'tour-route']) map.setPaintProperty(id, 'line-color', t.color);
    map.setPaintProperty('tour-stop', 'circle-stroke-color', t.color); map.setPaintProperty('tour-num', 'text-color', t.color);
  }
  for (const id of ['tour-route-glow', 'tour-route', 'tour-stop', 'tour-num']) map.setLayoutProperty(id, 'visibility', 'visible');
}
function markStop(k) {
  if (!map.getLayer('tour-stop')) return;
  // the current stop becomes an open ring, so the church's own pin and name show inside it
  const here = ['==', ['get', 'k'], k];
  map.setPaintProperty('tour-stop', 'circle-radius', ['case', here, 20, 10]);
  map.setPaintProperty('tour-stop', 'circle-color', ['case', here, 'rgba(0,0,0,0)', '#05070d']);
  map.setPaintProperty('tour-stop', 'circle-stroke-width', ['case', here, 2.5, 2]);
  map.setPaintProperty('tour-num', 'text-opacity', ['case', here, 0, 1]);
}
// on phones the stop is framed in the space left above the guide card (and the tab bar below it)
const tourPad = () => phone() ? { top: 120, bottom: (tourCard.hidden ? 260 : innerHeight - tourCard.getBoundingClientRect().top) + 30, left: 20, right: 20 } : { left: 400, right: 80, top: 120, bottom: 60 };
async function startTour(id) {
  const list = await loadTours(); const t = list.find(x => x.id === id); if (!t) return;
  ccf.track('tour/' + id);
  showTours(false); ccf.closeCard(); showToday(false, true);
  tour.spinWas = tour.t ? tour.spinWas : state.spinning;
  state.spinning = false; $('spin').setAttribute('aria-pressed', 'false');
  tour.t = t; tour.k = -1; tour.auto = true;
  document.body.classList.add('tour-on');
  tourLayers(t);
  try { history.replaceState(null, '', '?tour=' + t.id); } catch (e) {}
  // a look at the whole route first, then the first stop
  const b = t.stops.reduce((bb, s) => bb.extend([s.lon, s.lat]), new maplibregl.LngLatBounds([t.stops[0].lon, t.stops[0].lat], [t.stops[0].lon, t.stops[0].lat]));
  renderTourCard(-1);
  tour.flying = true;
  map.fitBounds(b, { padding: tourPad(), maxZoom: t.route ? 6.5 : 4, pitch: 0, bearing: 0, duration: reduceMotion ? 0 : 2600, essential: true });
  map.once('moveend', () => { tour.flying = false; if (tour.t === t) scheduleNext(reduceMotion ? 2500 : 3200); });
}
function renderTourCard(k) {
  const t = tour.t; if (!t) return;
  const s = t.stops[k];
  tourCard.style.setProperty('--tc', t.color);
  const play = tour.auto ? '<svg viewBox="0 0 24 24"><path d="M8 5v14M16 5v14"/></svg>' : '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l12-7.5z"/></svg>';
  const last = k === t.stops.length - 1;
  tourCard.innerHTML = `<button class="x" id="tourExit" aria-label="${esc(T('tourEnd'))}">${X}</button>
    <div class="kick"><b>${esc(t.title)}</b> · ${esc(k < 0 ? T('stops', { n: t.stops.length }) : T('stopOf', { k: k + 1, n: t.stops.length }))}</div>
    <h2><button class="more" aria-expanded="${tourCard.classList.contains('more')}">${esc(s ? s.name : t.title)}</button></h2>
    ${s ? `<div class="where">${esc(s.place)}</div>` : ''}
    <p>${esc(s ? s.text : t.sub + '.')}</p>
    <div class="dots" role="tablist" aria-label="${esc(T('stopsLabel'))}">${t.stops.map((x, j) => `<button data-k="${j}" aria-current="${j === k}" aria-label="${esc(T('stopName', { k: j + 1, name: x.name }))}" title="${esc(x.name)}"></button>`).join('')}</div>
    <div class="timer" aria-hidden="true"><i id="tourTimer"></i></div>
    <div class="nav">
      <button class="btn icon" id="tourPrev" aria-label="${esc(T('tourPrev'))}" ${k <= 0 ? 'disabled' : ''}><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></button>
      <button class="btn icon" id="tourPlay" aria-label="${esc(T(tour.auto ? 'tourPause' : 'tourPlay'))}" aria-pressed="${tour.auto}">${play}</button>
      ${s && s.i != null ? `<button class="btn" id="tourOpen">${esc(T('churchDetails'))}</button>` : ''}
      <span class="grow"></span>
      ${last ? `<button class="btn primary" id="tourDone">${esc(T('tourFinish'))}</button>` : `<button class="btn primary" id="tourNext">${esc(T(k < 0 ? 'tourBegin' : 'tourNext'))} <svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></button>`}
    </div>`;
  tourCard.hidden = false;
  document.documentElement.style.setProperty('--tour-h', tourCard.offsetHeight + 'px');
}
tourCard.addEventListener('click', (e) => {
  const b = e.target.closest('button'); if (!b || !tour.t) return;
  if (b.id === 'tourExit' || b.id === 'tourDone') endTour();
  else if (b.id === 'tourNext') goStop(tour.k + 1);
  else if (b.id === 'tourPrev') goStop(tour.k - 1);
  else if (b.id === 'tourPlay') { tour.auto = !tour.auto; renderTourCard(tour.k); if (tour.auto) scheduleNext(2000); else clearNext(); }
  else if (b.id === 'tourOpen') { clearNext(); tour.auto = false; renderTourCard(tour.k); ccf.selectChurch(tour.t.stops[tour.k].i, { fly: false }); }
  else if (b.dataset.k) goStop(+b.dataset.k);
  else if (b.classList.contains('more')) {  // phones show the story only when the title is tapped
    const on = tourCard.classList.toggle('more'); b.setAttribute('aria-expanded', on);
    document.documentElement.style.setProperty('--tour-h', tourCard.offsetHeight + 'px');
  }
});
function clearNext() { clearTimeout(tour.timer); cancelAnimationFrame(tour.raf); const bar = $('tourTimer'); if (bar) bar.style.width = '0'; }
function scheduleNext(ms) {
  clearNext();
  if (!tour.t || !tour.auto) return;
  const last = tour.k >= tour.t.stops.length - 1;
  if (last) return;
  tour.t0 = performance.now();
  const tick = (now) => { const bar = $('tourTimer'); if (bar) bar.style.width = Math.min(100, (now - tour.t0) / ms * 100) + '%'; if (now - tour.t0 < ms) tour.raf = requestAnimationFrame(tick); };
  tour.raf = requestAnimationFrame(tick);
  tour.timer = setTimeout(() => { if (tour.t && tour.auto && $('card').hidden) goStop(tour.k + 1); else if (tour.t && tour.auto) scheduleNext(4000); }, ms);
}
function goStop(k) {
  const t = tour.t; if (!t || k < 0 || k >= t.stops.length) return;
  clearNext(); tour.k = k;
  const s = t.stops[k];
  renderTourCard(k); markStop(k);
  if (!$('card').hidden) ccf.closeCard();
  tour.flying = true;
  const bearing = ((k * 47) % 120) - 60;
  map.flyTo({ center: [s.lon, s.lat], zoom: 13.6, pitch: 50, bearing, speed: 1.1, curve: 1.6, padding: tourPad(), essential: true, ...(reduceMotion ? { duration: 0 } : {}) });
  map.once('moveend', () => {
    tour.flying = false;
    if (tour.t !== t || tour.k !== k) return;
    // a slow turn around the church while the card is read
    if (!reduceMotion) map.easeTo({ bearing: bearing + 30, duration: tour.dwell + 4000, easing: (x) => x, padding: tourPad() });
    scheduleNext(tour.dwell);
  });
}
function endTour() {
  if (!tour.t) return;
  clearNext(); tour.t = null;
  tourCard.hidden = true; document.body.classList.remove('tour-on');
  for (const id of ['tour-route-glow', 'tour-route', 'tour-stop', 'tour-num']) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', 'none');
  if (tour.spinWas) $('spin').click();
  try { history.replaceState(null, '', location.pathname); } catch (e) {}
  map.flyTo({ center: [map.getCenter().lng, 25], zoom: phone() ? 1.6 : 2.2, pitch: 0, bearing: 0, duration: reduceMotion ? 0 : 2200 });
}
// dragging or zooming the globe pauses the tour; the guide waits until asked to go on
for (const ev of ['mousedown', 'touchstart', 'wheel']) map.on(ev, () => { if (tour.t && tour.auto && !tour.flying) { tour.auto = false; clearNext(); map.stop(); renderTourCard(tour.k); } });
addEventListener('keydown', (e) => {
  if (!tour.t || e.target.closest('input, textarea') || !$('lightbox').hidden) return;
  if (e.key === 'ArrowRight') goStop(tour.k + 1); else if (e.key === 'ArrowLeft') goStop(tour.k - 1);
  else if (e.key === 'Escape' && $('card').hidden && toursEl.hidden && $('favs').hidden && $('near').hidden) endTour();
});
// the details card and the tour guide share the bottom of a phone screen: the guide steps aside while the card is open
new MutationObserver(() => { if (tour.t && $('card').hidden && tour.auto) scheduleNext(4000); }).observe($('card'), { attributes: true, attributeFilter: ['hidden'] });

/* ---------- globe view: stars, atmosphere, day and night, satellite, density ---------- */
const menu = document.createElement('div');
menu.id = 'viewMenu'; menu.className = 'viewmenu'; menu.hidden = true; menu.setAttribute('role', 'dialog');
const SWITCHES = ['satellite', 'daynight', 'sky', 'density', 'liturgical'];
function renderMenu() {
  menu.setAttribute('aria-label', T('globeView'));
  menu.innerHTML = `<h3>${esc(T('globeView'))}</h3>` + SWITCHES.map(k => `<label><span>${esc(T('view_' + k))}</span><small>${esc(T('view_' + k + 'Hint'))}</small><input type="checkbox" data-k="${k}" ${view[k] ? 'checked' : ''}></label>`).join('');
}
renderMenu();
document.body.appendChild(menu);
function showMenu(open) {
  menu.hidden = !open; viewBtn.setAttribute('aria-expanded', open); viewBtn.setAttribute('aria-pressed', open);
  if (open && !phone() && viewBtn.offsetParent) {  // beside its button; on phones the button lives in the menu, so from the bottom
    const r = viewBtn.getBoundingClientRect();
    menu.style.right = (innerWidth - r.left + 10) + 'px'; menu.style.left = 'auto';
    menu.style.top = Math.max(12, Math.min(r.top - 40, innerHeight - menu.offsetHeight - 12)) + 'px'; menu.style.bottom = 'auto';
  } else if (open) { menu.style.top = 'auto'; menu.style.bottom = 'calc(40px + env(safe-area-inset-bottom, 0px))'; menu.style.right = ''; }
}
viewBtn.addEventListener('click', (e) => { e.stopPropagation(); showMenu(menu.hidden); });
addEventListener('pointerdown', (e) => { if (!menu.hidden && !e.target.closest('#viewMenu, #viewBtn')) showMenu(false); });
addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { e.stopImmediatePropagation(); showMenu(false); viewBtn.focus(); } }, true);
menu.addEventListener('change', (e) => {
  const k = e.target.dataset.k; if (!k) return;
  view[k] = e.target.checked; saveView(); applyView(k);
});

// stars: one tile drawn once, then slid about as the globe turns, so it costs nothing per frame
const stars = document.createElement('div');
stars.id = 'stars'; stars.setAttribute('aria-hidden', 'true');
$('stage').insertBefore(stars, $('map'));
function drawStars() {
  const S = 1024, c = document.createElement('canvas'); c.width = c.height = S;
  const g = c.getContext('2d');
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  // a faint band of the Milky Way across the tile
  for (let k = 0; k < 900; k++) {
    const x = rnd() * S, y = S * 0.5 + (x - S / 2) * 0.35 + (rnd() + rnd() + rnd() - 1.5) * 150;
    g.fillStyle = `rgba(${200 + rnd() * 55 | 0},${200 + rnd() * 40 | 0},255,${0.08 + rnd() * 0.22})`;
    g.fillRect(x, ((y % S) + S) % S, 1, 1);
  }
  for (let k = 0; k < 520; k++) {
    const x = rnd() * S, y = rnd() * S, m = rnd(), r = m > 0.985 ? 1.4 : m > 0.9 ? 0.9 : 0.55;
    const tint = rnd(); const col = tint > 0.92 ? '255,214,170' : tint > 0.84 ? '180,205,255' : '255,255,255';
    g.fillStyle = `rgba(${col},${0.35 + m * 0.6})`;
    g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
    if (r > 1) { g.fillStyle = `rgba(${col},0.12)`; g.beginPath(); g.arc(x, y, r * 3, 0, 7); g.fill(); }
  }
  stars.style.backgroundImage = `url(${c.toDataURL()})`;
  stars.style.backgroundSize = S + 'px ' + S + 'px';
  if (!reduceMotion) for (let k = 0; k < 14; k++) {
    const i = document.createElement('i');
    i.style.left = (rnd() * 100) + '%'; i.style.top = (rnd() * 100) + '%'; i.style.animationDelay = (-rnd() * 4).toFixed(2) + 's'; i.style.animationDuration = (3 + rnd() * 3).toFixed(2) + 's';
    stars.appendChild(i);
  }
}
let starRaf = 0;
function moveStars() {
  starRaf = 0;
  const c = map.getCenter(), z = map.getZoom();
  stars.style.backgroundPosition = `${(-c.lng * 4).toFixed(1)}px ${(c.lat * 3).toFixed(1)}px`;
  stars.style.transform = `rotate(${(-map.getBearing()).toFixed(2)}deg)`;
  stars.classList.toggle('off', !view.sky || z > 5.5);
}
map.on('move', () => { if (!starRaf) starRaf = requestAnimationFrame(moveStars); });
document.addEventListener('ccf-theme', () => { applySky(); if (map.getLayer('night') && ccf.nightOpacity) map.setPaintProperty('night', 'raster-opacity', ccf.nightOpacity()); });

// the atmosphere: a blue halo around the globe that thins out as you zoom into a city
function applySky() {
  try {
    const [sky, horizon, fog] = ccf.sky ? ccf.sky() : ['#0b1a36', '#2b4c80', '#0a1a33'];
    map.setSky(view.sky ? {
      'sky-color': sky, 'horizon-color': horizon, 'fog-color': fog,
      'sky-horizon-blend': 0.7, 'horizon-fog-blend': 0.6, 'fog-ground-blend': 0.9,
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 5, 1, 7, 0],
    } : { 'atmosphere-blend': 0, 'sky-color': '#05070d', 'horizon-color': '#05070d', 'fog-color': '#05070d' });
  } catch (e) {}
  moveStars();
}

// day and night: the shade is a small picture of the world, darkest where the sun is furthest below the horizon
function sunPosition(date) {
  const d = date.getTime() / 864e5 - 10957.5; // days from J2000
  const g = (357.529 + 0.98560028 * d) * rad, q = 280.459 + 0.98564736 * d;
  const L = (q + 1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g)) * rad, e = (23.439 - 0.00000036 * d) * rad;
  const ra = Math.atan2(Math.cos(e) * Math.sin(L), Math.cos(L)), dec = Math.asin(Math.sin(e) * Math.sin(L));
  const gmst = ((18.697374558 + 24.06570982441908 * d) % 24 + 24) % 24;
  let lon = (ra / rad - gmst * 15) % 360; if (lon > 180) lon -= 360; if (lon < -180) lon += 360;
  return { lat: dec / rad, lon };
}
const MERC = 85.051129;
const nightCanvas = document.createElement('canvas'); nightCanvas.width = 512; nightCanvas.height = 512;
function drawNight() {
  const W = nightCanvas.width, H = nightCanvas.height, g = nightCanvas.getContext('2d');
  const sun = sunPosition(new Date()), sd = sun.lat * rad;
  const img = g.createImageData(W, H), px = img.data;
  const sinD = Math.sin(sd), cosD = Math.cos(sd);
  const cosH = new Float32Array(W);
  for (let x = 0; x < W; x++) cosH[x] = Math.cos(((x + 0.5) / W * 360 - 180 - sun.lon) * rad);
  for (let y = 0; y < H; y++) {
    const lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * (y + 0.5) / H))), sl = Math.sin(lat) * sinD, cl = Math.cos(lat) * cosD;
    for (let x = 0; x < W; x++) {
      const alt = Math.asin(sl + cl * cosH[x]) / rad; // the sun's height above the horizon there
      const k = alt >= 0.8 ? 0 : alt <= -12 ? 1 : (0.8 - alt) / 12.8;
      const o = (y * W + x) * 4, f = k * k * (3 - 2 * k);
      // a faint blue light on the day side, deepening to night through twilight
      px[o] = 150 - 148 * f; px[o + 1] = 190 - 184 * f; px[o + 2] = 255 - 233 * f; px[o + 3] = Math.round(20 + f * 160);
    }
  }
  g.putImageData(img, 0, 0);
  return nightCanvas.toDataURL('image/png');
}
const NIGHT_COORDS = [[-180, MERC], [180, MERC], [180, -MERC], [-180, -MERC]];
let nightTimer = 0;
function applyNight() {
  clearInterval(nightTimer);
  if (!view.daynight) { if (map.getLayer('night')) map.setLayoutProperty('night', 'visibility', 'none'); return; }
  const url = drawNight();
  if (!map.getSource('night')) {
    map.addSource('night', { type: 'image', url, coordinates: NIGHT_COORDS });
    map.addLayer({ id: 'night', type: 'raster', source: 'night', paint: { 'raster-opacity': ccf.nightOpacity ? ccf.nightOpacity() : 1, 'raster-fade-duration': 0, 'raster-resampling': 'linear' } }, 'rivers');
  } else { map.getSource('night').updateImage({ url, coordinates: NIGHT_COORDS }); map.setLayoutProperty('night', 'visibility', 'visible'); }
  nightTimer = setInterval(() => { if (map.getSource('night') && !document.hidden) map.getSource('night').updateImage({ url: drawNight(), coordinates: NIGHT_COORDS }); }, 120000);
}

// satellite: Sentinel-2 cloudless by EOX, free for non-commercial use with credit
function applySatellite() {
  const on = view.satellite;
  if (on && !map.getSource('sat')) {
    map.addSource('sat', { type: 'raster', tiles: ['https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg'], tileSize: 256, maxzoom: 14, attribution: 'Sentinel-2 cloudless by EOX' });
    map.addLayer({ id: 'sat', type: 'raster', source: 'sat', paint: { 'raster-opacity': 1, 'raster-brightness-max': 0.88, 'raster-saturation': -0.05, 'raster-contrast': 0.05, 'raster-fade-duration': 250 } }, map.getLayer('night') ? 'night' : 'rivers');
  }
  if (map.getLayer('sat')) map.setLayoutProperty('sat', 'visibility', on ? 'visible' : 'none');
  for (const id of ['urban', 'lakes']) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'none' : 'visible');
  if (map.getLayer('land-edge')) map.setPaintProperty('land-edge', 'line-opacity', on ? 0.25 : 0.8);
  let credit = document.querySelector('.foot .imagery');
  if (!credit) {
    credit = document.createElement('span'); credit.className = 'imagery';
    credit.innerHTML = 'Imagery <a href="https://s2maps.eu" target="_blank" rel="noopener" style="color:inherit">Sentinel-2 cloudless</a> by EOX (Copernicus Sentinel data 2020)';
    document.querySelector('.foot .coords').before(credit);
  }
  credit.hidden = !on;
}

// density glow: a warm haze under the clusters where churches crowd together
function applyDensity() {
  if (!map.getLayer('density')) {
    map.addLayer({ id: 'density', type: 'heatmap', source: 'churches', maxzoom: 7, paint: {
      'heatmap-weight': ['interpolate', ['linear'], ['coalesce', ['get', 'point_count'], 1], 1, 0.04, 50, 0.25, 500, 0.5, 5000, 0.8],
      'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 0.5, 6, 0.9],
      'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 12, 3, 22, 6, 34],
      'heatmap-color': ['interpolate', ['linear'], ['heatmap-density'], 0, 'rgba(232,184,74,0)', 0.15, 'rgba(150,100,35,0.22)', 0.45, 'rgba(210,160,60,0.36)', 0.8, 'rgba(240,200,110,0.46)', 1, 'rgba(250,225,160,0.55)'],
      'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 0, 0.9, 4.5, 0.7, 6.5, 0],
    } }, 'cl-glow');
  }
  map.setLayoutProperty('density', 'visibility', view.density && !bibleMode() ? 'visible' : 'none');
}

// golden cathedrals: cathedrals and basilicas glow larger than other churches at every zoom
function pinImage(fill, ring) {
  const s = 64, c = document.createElement('canvas'); c.width = c.height = s;
  const g = c.getContext('2d'), m = s / 2;
  const glow = g.createRadialGradient(m, m, 8, m, m, m);
  glow.addColorStop(0, 'rgba(246,220,150,.55)'); glow.addColorStop(1, 'rgba(246,220,150,0)');
  g.fillStyle = glow; g.beginPath(); g.arc(m, m, m, 0, 7); g.fill();
  g.fillStyle = fill; g.strokeStyle = ring; g.lineWidth = 3.5;
  g.beginPath(); g.arc(m, m, 15, 0, 7); g.fill(); g.stroke();
  g.strokeStyle = fill === '#f6e7b4' ? '#6b4a12' : '#fff6dc'; g.lineWidth = 3.4; g.lineCap = 'round';
  g.beginPath(); g.moveTo(m, m - 9); g.lineTo(m, m + 9); g.moveTo(m - 6, m - 3); g.lineTo(m + 6, m - 3); g.stroke();
  return g.getImageData(0, 0, s, s);
}
function goldenPins() {
  if (map.getLayer('notable-glow')) return;
  map.addImage('pin-cathedral', pinImage('#d2484f', '#f6dc96'), { pixelRatio: 2 });
  map.addImage('pin-basilica', pinImage('#f6e7b4', '#e8b84a'), { pixelRatio: 2 });
  map.setLayerZoomRange('notable', 1.2, 10);
  map.setPaintProperty('notable', 'circle-radius', ['interpolate', ['linear'], ['zoom'], 1.2, 1.6, 4, 2.8, 7, 4.5, 10, 6.5]);
  map.setPaintProperty('notable', 'circle-opacity', ['interpolate', ['linear'], ['zoom'], 1.2, 0.95, 9.5, 0.95, 10, 0]);
  map.setPaintProperty('notable', 'circle-stroke-color', '#f6dc96');
  map.setPaintProperty('notable', 'circle-stroke-width', ['interpolate', ['linear'], ['zoom'], 1.2, 0.4, 6, 1.2]);
  map.setPaintProperty('notable', 'circle-stroke-opacity', 0.9);
  map.addLayer({ id: 'notable-glow', type: 'circle', source: 'notable', minzoom: 1.2, paint: {
    'circle-color': ['match', ['get', 't'], 1, '#ff7a6e', '#f6dc96'], 'circle-blur': 1,
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 1.2, 3.5, 4, 6, 8, 13, 14, 24],
    'circle-opacity': ['interpolate', ['linear'], ['zoom'], 1.2, 0.22, 5, 0.3, 8, 0.45, 14, 0.4],
  } }, 'notable');
  map.addLayer({ id: 'notable-pin', type: 'symbol', source: 'notable', minzoom: 9.5, layout: {
    'icon-image': ['match', ['get', 't'], 1, 'pin-cathedral', 'pin-basilica'],
    'icon-size': ['interpolate', ['linear'], ['zoom'], 9.5, 0.75, 13, 1, 17, 1.3], 'icon-allow-overlap': true, 'icon-ignore-placement': true,
  }, paint: { 'icon-opacity': ['interpolate', ['linear'], ['zoom'], 9.5, 0, 10, 1] } }, 'hover');
}

function applyView(k) {
  if (!k || k === 'sky') applySky();
  if (!k || k === 'daynight') applyNight();
  if (!k || k === 'satellite') applySatellite();
  if (!k || k === 'density') applyDensity();
  if (!k || k === 'liturgical') applySeason();
}

/* ---------- Bible Places mode: the church-only extras step aside ---------- */
const bibleMode = () => document.body.classList.contains('bible-mode');
new MutationObserver(() => {
  const on = bibleMode();
  if (on) { endTour(); showTours(false); showToday(false, true); }
  for (const id of ['notable-glow', 'notable-pin']) if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'none' : 'visible');
  if (map.getLayer('density')) map.setLayoutProperty('density', 'visibility', !on && view.density ? 'visible' : 'none');
}).observe(document.body, { attributes: true, attributeFilter: ['class'] });

/* ---------- start ---------- */
drawStars(); moveStars();
ccf.layers.then(() => {
  try { goldenPins(); } catch (e) { console.warn('golden pins', e); }
  try { applyView(); } catch (e) { console.warn('globe view', e); }
});
const todayReady = (i18n && i18n.ready ? i18n.ready.catch(() => {}) : Promise.resolve()).then(() => { relabel(); return initToday(); }).catch((e) => console.warn('today', e));
function relabel() {
  for (const [b, k] of [[tourBtn, 'tours'], [viewBtn, 'globeView']]) { b.title = T(k); b.setAttribute('aria-label', T(k)); }
  $('toursTitle').textContent = T('tours'); $('toursClose').setAttribute('aria-label', T('toursClose')); $('toursNote').textContent = T('toursNote');
  tourCard.setAttribute('aria-label', T('tourGuide'));
  renderMenu();
}
document.addEventListener('ccf-lang', () => {
  relabel();
  if (today) { seasonPill(); if ($('today')) $('today').setAttribute('aria-label', T('todayLabel')); if (cal && cotd) fillToday(); }
  if (!toursEl.hidden) renderTourList();
  if (tour.t) renderTourCard(tour.k);
});
ccf.opened.then(async ({ shared }) => {
  const tourId = new URLSearchParams(location.search).get('tour');
  if (tourId && !bibleMode()) { startTour(tourId); return; }
  await todayReady;
  let closed = null; try { closed = localStorage.getItem(TODAY_KEY); } catch (e) {}
  // church of the day slides in once the globe has settled over the United States, unless closed earlier today;
  // phones keep the globe clear and offer it on the Today button instead
  if (!shared && !bibleMode() && !compact() && cotd && closed !== String(today.n)) setTimeout(() => { if (!tour.t && $('card').hidden) showToday(true, true); }, reduceMotion ? 300 : 3600);
});
})();
