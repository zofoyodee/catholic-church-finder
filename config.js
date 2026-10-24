// Sign-in service settings. Both values are public by design: the anon key only
// allows what the row-level security rules in supabase/schema.sql allow.
// Never put the service_role key here.
// Leave them empty and the site runs without accounts (favorites stay in this browser).
window.CCF_SUPABASE = {
  url: '',      // e.g. 'https://abcdefghijklmno.supabase.co'
  anonKey: ''   // the "anon public" key from Project Settings > API
};
