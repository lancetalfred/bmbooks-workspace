# Bruce McKenzie Booksellers — Website Summary
**Prepared by Lance Alfred | March 2026**

---

## Website Overview

| Detail | Info |
|--------|------|
| Website | bmbooks.co.nz |
| Platform | WordPress + WooCommerce |
| Theme | Divi |
| PHP Version | 8.1 |

---

## Who Manages What

| Asset | Company | Contact | Notes |
|-------|---------|---------|-------|
| Domain registration | Black Sheep Design | Abbey Paton — abbey@bsd.nz | Renews domain yearly. Abbey is helpful and responsive. |
| Domain nameservers | Black Sheep Design | Abbey Paton — abbey@bsd.nz | Currently pointing to Cloudflare (updated March 2026) |
| Web hosting | Barcode Solutions (A2 Hosting) | Shanti Ratnam — shanti@bookscan.com.au | A2 Hosting account is in Shanti's name, not Louisa's. This is a risk. |
| Cloudflare CDN | Cloudflare | Lance Alfred account (to be transferred to Louisa) | Free plan. Set up March 2026. |
| Website backup | UpdraftPlus → Google Drive | Currently Lance's Google Drive (to be moved to Louisa's) | Backup includes database, plugins, themes. |

---

## Hosting Details

| Detail | Info |
|--------|------|
| Hosting provider | A2 Hosting |
| Server location | Singapore |
| Server type | LiteSpeed |
| Control panel | cPanel |
| Server address | sg1-tr1.supercp.com |
| IP address | 85.187.128.38 |
| Email provider | Spark Business Mail (separate from hosting) |

---

## Important Risks

1. **Hosting account not in Louisa's name** — The A2 Hosting account is registered under Barcode Solutions (Shanti). If the relationship ends badly, Shanti could hold the website hostage. Recommended fix: open a direct A2 Hosting account in Louisa's name and migrate.

2. **Backup not in Louisa's Google Drive** — Currently backed up to Lance's personal Google Drive. Needs to be moved to Louisa's Google account as soon as possible.

3. **27GB mystery backup file on server** — A file called backup-3.6.2026_11-27-04_bmbooksconz.tar.gz (27.65GB) exists in the home directory. Likely created by Shanti. Awaiting confirmation before deleting.

---

## Performance Improvements Made (March 2026)

| Improvement | Details |
|-------------|---------|
| Cloudflare CDN | Set up on free plan. Nameservers updated by Abbey at Black Sheep Design. |
| LiteSpeed Cache | Installed and configured. Two layers of caching now active. |
| Cloudflare Fonts | Enabled — Google Fonts now served locally, no external requests. |
| Cloudflare Speed | HTTP/2, HTTP/3, 0-RTT, Early Hints, Speed Brain, Rocket Loader all enabled. |
| WooCommerce cache bypass | Cart, checkout and my-account pages excluded from caching. |
| Cart fragments disabled | WooCommerce cart fragments script disabled (was blocking page load). |
| LCP image preload | Hero image preloaded for faster mobile load times. |
| Imagify WebP | Converting product images to WebP format (in progress). |
| Disk space freed | Removed ~30GB of old backups and staging files. Server healthy. |

---

## Cloudflare Account

- **Account holder:** Lance Alfred (lancealfred@hotmail.com) — needs to be transferred to Louisa
- **Plan:** Free
- **Nameservers:** ignat.ns.cloudflare.com / zara.ns.cloudflare.com
- **To transfer:** Cloudflare dashboard → My Profile → Account → Transfer

---

## Backup Status

| Component | Backed up? | Location |
|-----------|-----------|---------|
| Database | Yes | Google Drive (Lance's — move to Louisa's) |
| Plugins | Yes | Google Drive (Lance's — move to Louisa's) |
| Themes | Yes | Google Drive (Lance's — move to Louisa's) |
| Uploads (images) | No | Too large for current server to back up via UpdraftPlus. Priority: lower. |

**To move backup to Louisa's Google Drive:**
1. WordPress admin → UpdraftPlus → Settings
2. Google Drive section → Revoke token
3. Re-authenticate with Louisa's Google account
4. Run a fresh backup

---

## WordPress Plugins (Key)

| Plugin | Status | Purpose |
|--------|--------|---------|
| LiteSpeed Cache | Active | Server-side caching |
| Imagify | Active | WebP image optimisation |
| UpdraftPlus | Active | Backups to Google Drive |
| WooCommerce | Active | Online store |
| WooPayments | Active | Payment processing |
| Yoast SEO | Active | Search engine optimisation |
| Disable Cart Fragments | Active | Performance — stops AJAX cart blocking load |
| FiboSearch Pro | Active | Product search |
| WP Rocket | Inactive | No valid licence — can be deleted |

---

## To Do (Pending)

- [ ] Move UpdraftPlus backup to Louisa's Google Drive
- [ ] Transfer Cloudflare account to Louisa's email
- [ ] Confirm with Shanti whether 27GB .tar.gz backup can be deleted
- [ ] Resume and complete Imagify bulk optimisation
- [ ] Discuss longer term: move hosting to account in Louisa's name
- [ ] Consider Shopify migration (same setup as Hedley's Books) — check Bookscan compatibility first

---

## Comparison: bmbooks.co.nz vs hedleysbooks.co.nz

| | Bruce McKenzie Books | Hedley's Books |
|--|---------------------|----------------|
| Platform | WordPress + WooCommerce | Shopify |
| CDN | Cloudflare (just added) | Cloudflare |
| Hosting | A2 Hosting (via reseller) | Shopify hosted |
| Domain registrar | SiteName (via Black Sheep) | SiteName |
| Ownership | Partial risk (hosting in vendor name) | Full ownership |

---

## Key Contacts

| Name | Company | Email | Role |
|------|---------|-------|------|
| Louisa McKenzie | Bruce McKenzie Booksellers | books@bmbooks.co.nz | Owner |
| Abbey Paton | Black Sheep Design | abbey@bsd.nz | Domain manager |
| Shanti Ratnam | Barcode Solutions | shanti@bookscan.com.au | Hosting vendor |
| Lance Alfred | — | lancealfred@hotmail.com | Web developer |
