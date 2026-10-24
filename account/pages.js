/* Shared bits for login.html, signup.html and reset.html. */
(function () {
  const $ = (id) => document.getElementById(id);

  // "Show" buttons next to password fields
  document.querySelectorAll('button.show').forEach((b) => {
    b.addEventListener('click', () => {
      const input = b.previousElementSibling;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      b.textContent = show ? 'Hide' : 'Show';
      b.setAttribute('aria-pressed', show);
    });
  });

  function say(text, kind) {
    const m = $('msg');
    m.className = 'msg ' + (kind || 'err');
    m.textContent = text || '';
    m.setAttribute('role', kind === 'ok' ? 'status' : 'alert');
  }

  // Runs a form action with the button disabled and errors shown in plain words.
  async function busy(button, label, fn) {
    const was = button.textContent;
    button.disabled = true; button.textContent = label;
    say('');
    try { await fn(); }
    catch (err) { say(CCFAuth.friendly(err)); }
    finally { button.disabled = false; button.textContent = was; }
  }

  // Where to go after signing in: back to the page that sent us here, if it was on this site.
  function next() {
    const n = new URLSearchParams(location.search).get('next');
    if (n) { try { const u = new URL(n, CCFAuth.home); if (u.origin === location.origin && u.href.startsWith(CCFAuth.home)) return u.href; } catch (e) {} }
    return CCFAuth.home;
  }

  if (!CCFAuth.configured) {
    document.querySelectorAll('form').forEach((f) => f.querySelectorAll('input, button').forEach((el) => { el.disabled = true; }));
    say('Accounts are not switched on for this site yet. You can still save favorites in this browser from the globe.');
  }

  window.CCFPage = { $, say, busy, next };
})();
