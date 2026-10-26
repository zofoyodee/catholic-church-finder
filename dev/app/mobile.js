/* Phones: the globe gets the screen. A search bar on top, the three tabs and a Menu button along
   the bottom, and everything else (filters, Church Near Me, language, theme, tours, about) in one
   menu sheet. The same page elements are moved into the sheet, so their own handlers keep working,
   and moved back when the screen grows. Computers get the same layout (html.wide, app/desktop.css):
   the tabs and Menu float in a bar along the bottom, and the filters, language and theme live in the menu. */
(() => {
'use strict';
const $ = (id) => document.getElementById(id);
const compact = matchMedia('(max-width: 640px), (max-height: 500px) and (orientation: landscape)');
const sheet = $('msheet');
if (!sheet) return;

// what moves into the sheet, and where it goes; a marker keeps each one's place on the page.
// 'all' moves on every screen; the rest only on phones.
const MOVES = [
  [() => document.querySelector('.brand'), 'msHead'],
  [() => $('chips'), 'msShow', 'all'],
  [() => $('massChips'), 'msMass', 'all'],
  [() => document.querySelector('.langpick'), 'msPicks', 'all'],
  [() => document.querySelector('.themepick'), 'msPicks', 'all'],
  [() => document.querySelector('footer.foot'), 'msFoot'],
];
const marks = new Map();
function place() {
  const small = compact.matches;
  document.documentElement.classList.toggle('compact', small);
  document.documentElement.classList.toggle('wide', !small);
  for (const [get, box, all] of MOVES) {
    const el = get(); if (!el) continue;
    if (small || all) {
      if (!marks.has(el)) { const m = document.createComment('mobile'); el.before(m); marks.set(el, m); }
      if (el.parentNode !== $(box)) $(box).appendChild(el);
    } else if (marks.has(el)) { marks.get(el).replaceWith(el); marks.delete(el); }
  }
  show(false);
}
compact.addEventListener('change', place);
place();

/* ---------- the menu sheet ---------- */
function show(open) {
  sheet.hidden = !open;
  $('mnavMenu').setAttribute('aria-expanded', open);
  document.documentElement.classList.toggle('ms-open', open);
  if (open) sync();
}
function sync() {
  // only offer what the page offers right now: favorites once there are some
  for (const b of sheet.querySelectorAll('.ms-acts button[data-for]')) {
    const t = $(b.dataset.for);
    b.hidden = !t || (b.dataset.for === 'favOpen' && t.hidden);
    if (b.dataset.for === 'favOpen' && t) { const n = t.querySelector('.count'); b.dataset.n = n ? n.textContent : ''; }
    if (t && t.getAttribute('aria-pressed')) b.setAttribute('aria-pressed', t.getAttribute('aria-pressed'));
  }
  // My Churches lists the saved churches, or says how to save one
  const none = !$('favOpen') || $('favOpen').hidden;
  for (const el of sheet.querySelectorAll('.ms-mine')) el.hidden = none;
  for (const el of sheet.querySelectorAll('.ms-empty')) el.hidden = !none;
}
const toggle = () => show(sheet.hidden);
$('mnavMenu').addEventListener('click', toggle);
$('msClose').addEventListener('click', () => show(false));
sheet.addEventListener('click', (e) => { if (e.target === sheet) show(false); });  // tap outside the box
addEventListener('keydown', (e) => { if (e.key === 'Escape' && !sheet.hidden) { show(false); $('mnavMenu').focus(); } });
sheet.addEventListener('click', (e) => {
  const b = e.target.closest('.ms-acts button[data-for]'); if (!b) return;
  show(false);
  const t = $(b.dataset.for); if (t) t.click();
});
// whatever the sheet opens (a list, a card, the church of the day, globe view) gets the screen
{
  const opened = () => { if (!sheet.hidden) show(false); };
  const watch = new MutationObserver((recs) => { if (recs.some(r => !r.target.hidden)) opened(); });
  const ids = ['card', 'near', 'favs', 'tours', 'today', 'viewMenu', 'about'];
  const hook = () => { for (const id of ids) if ($(id) && !$(id).dataset.mWatched) { $(id).dataset.mWatched = 1; watch.observe($(id), { attributes: true, attributeFilter: ['hidden'] }); } };
  hook();
  setTimeout(hook, 4000);  // the church of the day card is built once the calendar loads
}

// the Menu tab shows how many churches are saved, so Favorites can be found
{
  const n = () => { $('mnavMenu').dataset.n = $('favCount').textContent; };
  new MutationObserver(n).observe($('favCount'), { childList: true, characterData: true, subtree: true });
  n();
}

// Whole Globe lives at the end of the search bar on phones, where no panel ever covers it
$('globeBtn').addEventListener('click', () => { show(false); $('home').click(); });

/* ---------- bottom tabs: the same buttons as the desktop tabs ---------- */
const tabs = [...$('mnav').querySelectorAll('button[data-mode]')];
for (const b of tabs) b.addEventListener('click', () => { show(false); $(b.dataset.mode).click(); });
const mirror = () => { for (const b of tabs) b.setAttribute('aria-pressed', $(b.dataset.mode).getAttribute('aria-selected')); };
new MutationObserver(mirror).observe(document.querySelector('.modes'), { subtree: true, attributes: true, attributeFilter: ['aria-selected'] });
mirror();
})();
