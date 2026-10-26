# Contact Us form

The site's **Contact** button opens a form. When a visitor presses **Send Message**, the form posts to a small
Cloudflare Worker (`worker.js`), which:

1. turns away messages with profanity and asks the visitor to rephrase (a hidden field and a rate limit of
   3 messages a minute per address keep robots out);
2. has Cloudflare's built-in AI (Workers AI, Llama 3.3 70B) read the message: what kind it is, how urgent,
   which church it is about, a short summary and what the owner should do next;
3. writes an automatic reply in the visitor's language, in a Catholic voice, shows it on screen and, if they gave
   an address, emails it to them from `hello@churchglobe.com`. Spam and abusive messages get no reply;
4. emails the owner a summary through Resend, with a **Write Back** button. That opens a private page where the
   owner types an answer, which goes out from `hello@churchglobe.com`.

The owner's own email address is a private Worker setting. It is never in this repository, never sent to the
page, and never put on an email a visitor receives. Visitors who reply to `hello@churchglobe.com` reach the owner
through Namecheap's email forwarding.

The form stays hidden on the site until `CONTACT_API` near the top of the contact section of `index.html` is
set to the Worker's address.

## Cost

Everything here is on free plans: Cloudflare Workers (100,000 requests a day), Workers AI (a free daily allowance
of 10,000 "neurons", which covers far more messages than a contact form gets), and Resend (3,000 emails a month,
100 a day). Nothing needs a credit card.

## One-time setup

### 1. Resend: sending email from churchglobe.com

1. Sign up at <https://resend.com> (free).
2. **Domains > Add Domain**, enter `churchglobe.com`. Resend lists a few DNS records (an MX and TXT record on
   `send.churchglobe.com`, and a DKIM TXT record).
3. At Namecheap: **Domain List > churchglobe.com > Manage > Advanced DNS**, add each record exactly as Resend shows
   it. Back in Resend press **Verify**. It can take up to an hour.
4. **API Keys > Create API Key**, permission "Sending access", domain churchglobe.com. Copy the key (it starts with
   `re_`). It is shown only once.

### 2. Namecheap: forwarding hello@churchglobe.com to your inbox

At Namecheap: **Domain List > churchglobe.com > Manage > Mail Settings**, choose **Email Forwarding**, and add
`hello` forwarding to your own address. Visitors who answer an auto-reply land in your inbox; your address stays
hidden from them as long as you answer through the Write Back button rather than your own email's Reply.

### 3. Cloudflare: the Worker

1. Sign up at <https://dash.cloudflare.com/sign-up> (free). The site and its DNS stay where they are.
2. Open **Workers & Pages** once and pick a `workers.dev` subdomain when asked.
3. Copy your **Account ID** (shown on the Workers & Pages overview, right-hand side).
4. **My Profile > API Tokens > Create Token**, use the **Edit Cloudflare Workers** template, then
   **Continue to summary > Create Token**. Copy the token.

### 4. GitHub: private settings and deploy

In this repository: **Settings > Secrets and variables > Actions > New repository secret**. Add four secrets:

| Name | Value |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | the token from step 3 |
| `CLOUDFLARE_ACCOUNT_ID` | the account ID from step 3 |
| `RESEND_API_KEY` | the `re_` key from step 1 |
| `OWNER_EMAIL` | the address the summaries go to |

Then **Actions > Deploy Contact Us worker > Run workflow**. When it finishes, its log shows the Worker's address,
`https://churchglobe-contact.<your-subdomain>.workers.dev`. Put that address in `CONTACT_API` in `index.html` and the
Contact button appears on the site.

Repository secrets are never shown in public, in logs or to people viewing the repository.

## Optional: a robot check

If spam gets through, add Cloudflare Turnstile (free): **Turnstile > Add widget** for `churchglobe.com`, put the
site key in `TURNSTILE_SITEKEY` in `index.html`, and add the secret key as a Worker secret named `TURNSTILE_SECRET`.

## Changing things

- The AI's instructions, including how the auto-reply should sound, are `SYSTEM` in `worker.js`.
- The profanity lists are `ROOTS` and `WORDS` in `worker.js`.
- The sending address and allowed sites are `[vars]` in `wrangler.toml`.
- Messages, AI errors and email errors appear under the Worker's **Logs** tab in Cloudflare.
