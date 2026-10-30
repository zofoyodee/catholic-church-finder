// Offline support: every file the site loads is kept after its first use and served from the
// cache while a fresh copy is fetched in the background. The page itself prefers the network.
const CACHE = 'ccf-v100';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'data/meta.json', 'icons/icon-192.png'];
const CDN = /^https:\/\/cdn\.jsdelivr\.net\/npm\//;

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || req.headers.has('range')) return; // photo slices are byte ranges; let them through
  const mine = url.origin === location.origin;
  if (!mine && !CDN.test(req.url)) return; // Wikimedia lookups and fonts go straight to the network
  if (/\/admin\.html$/.test(url.pathname)) return; // the stats page is never kept offline or mistaken for the globe
  if (mine && /^\/dev\//.test(url.pathname)) return; // the test copy at /dev/ is never kept offline or mistaken for the globe
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); return res; })
      .catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.open(CACHE).then(async (c) => {
    const hit = await c.match(req, { ignoreSearch: mine });
    const fresh = fetch(req).then(res => { if (res.ok) c.put(req, res.clone()); return res; });
    if (hit) { e.waitUntil(fresh.catch(() => {})); return hit; }
    return fresh;
  }));
});
