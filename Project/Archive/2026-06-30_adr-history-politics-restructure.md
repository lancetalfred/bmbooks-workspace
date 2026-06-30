# ADR: History vs Politics Category Restructure

**Status:** Proposed — deferred to post-go-live
**Date:** 2026-06-30
**Decision owner:** Louisa (BookScan data), Lance (Shopify collections)

ADR format adapted from ECC's `architect` agent (github.com/affaan-m/ECC) — the template was worth keeping, the rest of that agent file (Next.js/Supabase/CQRS boilerplate) wasn't relevant.

## Context

During the category management audit (2026-06-20), we found that BookScan's "History And Politics" maincat assigns most products **both** the "History" and "Politics" subcat tags rather than one or the other:

- History subcat: 2,975 products
- Politics subcat: 2,743 products
- Overlap (tagged both): ~2,732 products — i.e. nearly all of Politics is also tagged History

A standalone "Politics" Shopify collection was proposed (2,736 products is large enough to justify one — bigger than several existing standalone collections like Crime & Thriller at 1,576). But creating it as-is would show a near-identical product set to the existing "History" collection, which defeats the purpose of separating them.

## Decision

**Defer creating a standalone Politics collection until the underlying BookScan tagging is cleaned up.** Logged as an action item for Louisa to review products in the History And Politics maincat and assign each to History OR Politics (or both, only where genuinely applicable — e.g. a book that is explicitly about the history of a political movement).

## Consequences

**Positive:**
- Avoids shipping a Shopify collection that doesn't actually solve the customer browsing problem it's meant to solve
- Forces the fix at the source (BookScan) rather than papering over it with a smarter Shopify tag rule, which would only mask the underlying data quality issue

**Negative:**
- Politics remains un-browsable as its own collection until Louisa completes the manual review — no firm timeline
- ~2,700 products stay only reachable via the broader History & Politics umbrella (2,730 products) in the meantime

## Alternatives considered

1. **Create the Politics collection anyway, accept the overlap** — rejected. Two collections showing nearly the same books is worse UX than one combined collection; customers would notice and trust the site less.
2. **Use a smarter Shopify-side rule to fake the split** (e.g. exclude products also tagged History) — rejected. Would require guessing which tag is the One True Category per product without manual review, likely getting it wrong for genuinely dual-topic books, and wouldn't fix the source data for future BookScan-tagged products.
3. **Leave as a single "History & Politics" collection permanently, don't pursue a split** — considered but not chosen. Politics at 2,736 products is large enough, and standalone everywhere in the industry (BISAC, Thema, Whitcoulls, Waterstones, Paper Plus), to be worth the standalone collection once the data supports it.

## Follow-up (once BookScan cleanup is done)
1. Create standalone "Politics" smart collection (tag=Politics)
2. Add both "History" and "Politics" tags to the Non-Fiction umbrella collection rules

See also: `Reports/category_audit.csv`, `Project/Active/BMBooks_Action_Items.md` ("BookScan cleanup: History vs Politics subcat overlap").
