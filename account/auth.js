/* Accounts for Catholic Church Finder, on Supabase Auth.
   Loaded by index.html and the sign-in pages after config.js. The Supabase library is only
   fetched when it is needed, so visitors who never sign in download nothing extra. */
(function () {
  const cfg = window.CCF_SUPABASE || {};
  const configured = !!(cfg.url && cfg.anonKey);
  const SDK = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js';
  const home = new URL('./', document.baseURI).href; // the site root, wherever it is hosted
  let clientP = null;

  function client() {
    if (!configured) return Promise.reject(new Error('Accounts are not set up on this site yet.'));
    if (!clientP) clientP = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = SDK;
      s.onload = () => resolve(window.supabase.createClient(cfg.url, cfg.anonKey, {
        auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
      }));
      s.onerror = () => { clientP = null; reject(new Error('The sign-in service did not load. Check your connection and try again.')); };
      document.head.appendChild(s);
    });
    return clientP;
  }

  // True when this browser holds a saved session, or the page was opened from an email link.
  function maybeSignedIn() {
    if (!configured) return false;
    if (/access_token=|error_description=|type=recovery/.test(location.hash)) return true;
    try {
      for (let k = 0; k < localStorage.length; k++) {
        const key = localStorage.key(k);
        if (/^sb-.*-auth-token$/.test(key)) return true;
      }
    } catch (e) {}
    return false;
  }

  async function session() {
    if (!maybeSignedIn()) return null;
    const db = await client();
    const { data } = await db.auth.getSession();
    return data.session;
  }

  function displayName(user) {
    if (!user) return '';
    const m = user.user_metadata || {};
    return (m.name || m.full_name || (user.email || '').split('@')[0] || 'Friend').trim();
  }

  // Supabase messages, in plain words.
  function friendly(err) {
    const msg = (err && err.message) || String(err || '');
    if (/invalid login credentials/i.test(msg)) return 'That email and password do not match. Try again, or reset your password.';
    if (/email not confirmed/i.test(msg)) return 'Please confirm your email first. Look for the message we sent when you created your account.';
    if (/already registered|already been registered/i.test(msg)) return 'An account with that email already exists. Sign in instead.';
    if (/rate limit|too many/i.test(msg)) return 'Too many tries. Please wait a few minutes and try again.';
    if (/password should be at least/i.test(msg)) return 'Please use a password of at least 8 characters.';
    if (/failed to fetch|network/i.test(msg)) return 'Could not reach the sign-in service. Check your connection and try again.';
    return msg || 'Something went wrong. Please try again.';
  }

  window.CCFAuth = { configured, home, client, maybeSignedIn, session, displayName, friendly };
})();
