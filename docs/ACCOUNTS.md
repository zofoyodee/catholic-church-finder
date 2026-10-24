# Accounts and synced favorites

Visitors can use the globe without an account; their favorites stay in that browser.
With an account, favorites are saved online and show up on every device they sign in on.
Accounts run on [Supabase](https://supabase.com) (free plan), because GitHub Pages cannot store data.

Pages: `login.html` (sign in), `signup.html` (create account), `reset.html` (forgot password).
Once signed in, the person's name appears at the top right of the globe, with a menu to sign out.

## How favorites move

- Signed out: favorites are kept in this browser only (as before).
- First sign-in on a browser: favorites already saved there are added to the account.
- Signed in: every Save or Remove is written to the account, and the account's list is loaded on each visit.
- Sign out: the browser's copy is cleared, so a shared computer does not keep someone's list.

## One-time setup (about 10 minutes)

1. Go to https://supabase.com, click **Start your project**, and sign in (GitHub sign-in is easiest).
2. Click **New project**. Name it `catholic-church-finder`, set a database password (save it somewhere; the site never needs it), pick the region closest to most visitors, and click **Create new project**. Wait a minute for it to finish.
3. In the left sidebar open **SQL Editor**, click **New query**, paste everything in [`supabase/schema.sql`](../supabase/schema.sql), and click **Run**. It should say "Success. No rows returned".
4. In the sidebar open **Authentication > URL Configuration**:
   - **Site URL**: `https://zofoyodee.github.io/catholic-church-finder/`
   - Under **Redirect URLs** click **Add URL** and add `https://zofoyodee.github.io/catholic-church-finder/**`
   - Click **Save**.
5. Optional, **Authentication > Emails**: edit the "Confirm signup" and "Reset password" templates so they mention Catholic Church Finder.
6. Open **Project Settings > API** (sometimes shown as **Data API** and **API Keys**). Copy:
   - the **Project URL** (looks like `https://abcdefghijklmno.supabase.co`)
   - the **anon public** key (a long string starting with `eyJ`, or a new-style `sb_publishable_...` key)
7. Put both into [`config.js`](../config.js) and push. Do **not** use the `service_role` / secret key; it must never be in this repo.

The anon key is safe to publish: the row-level security rules in `schema.sql` mean a signed-in person can only read and change their own favorites.

## Good to know

- Supabase's built-in email sender only sends a few emails per hour. That is fine for testing; for real traffic, add an SMTP provider under **Project Settings > Authentication > SMTP** (Resend, Brevo and others have free tiers).
- Free Supabase projects pause after a week with no activity; any visit to the dashboard or a sign-in wakes them.
- Favorites are stored by church number in `data/points.txt`. If the church data is rebuilt in a different order, saved favorites would point at different churches.
