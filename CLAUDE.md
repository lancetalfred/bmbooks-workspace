# BMBooks Workspace

## Project state
BMBooks (Bruce McKenzie Booksellers, 37 George Street, Palmerston North NZ).
Shopify migration from WooCommerce. Grow plan. Password-protected at bmbooks.co.nz.
Phase: pre-go-live, waiting on Louisa to confirm date. Technical work complete.
Sync: hourly bookscan_sync.py on shop machine (Windows, Chrome Remote Desktop).

## Start here
- Open tasks: `Project/Active/BMBooks_Action_Items.md`
- Release log: `Project/Active/BMBooks_Release_Notes.md`
- Decisions/completed work: `Project/Archive/`
- Tool workflows: `Tools/`

## Critical rules
1. NEVER push `templates/*.json` from local — pull first: `shopify theme pull --only templates/file.json`
   Theme Editor changes live on Shopify only. Pushing stale local JSON caused homepage 404 on 2026-06-12.
2. Before ANY push to staging (targeted or full), staging must already be in sync with production.
   If unsure: full pull from production → full push to staging → then apply your targeted change.
   Sequence: `shopify theme pull --theme 149898395726` → `shopify theme push --theme 150391423054`
   Root cause: pushing a single file to a stale staging theme causes 404s (missing files staging never had).
3. NEVER commit: `Sync/SABSSAVE/`, `Sync/*.dbf`, `Reports/`, `Sync/sync_state.json`, `.env`, `*.log`
4. NEVER read `Sync/bookscan_sync.log` or `*.dbf` in full — grep only (large/binary)
5. Shopify CLI must run from `Shopify_Theme/` directory (reads `shopify.theme.toml` from there)
6. Long-running scripts (bulk API updates, data fixes, enrichment runs) — give the user the command to run in their own terminal, don't run in background. Use `python3 -u` for unbuffered output.
   Root cause: Python buffers stdout when not connected to a terminal, so progress output doesn't appear until completion.

## Before you execute
1. **Verify first.** Before starting any work, state what you think we're doing and why — one or two sentences. Wait for confirmation.
2. **On anything non-trivial, use an agent to pressure-test the approach** — catch gaps, missing questions, and assumptions before building. The agent should challenge the plan, not just validate it.
3. **Changes to sync scripts** (`bookscan_sync.py`, `genre_enrichment_v2.py`, `bookkeeper_gui.py`) require deployment to the shop machine and testing before marking done.

## Code quality standards
All AI-generated code must adhere to industry best practices across three core areas:

**Security patterns:**
- Validate all user input at system boundaries (forms, API calls, external integrations)
- Never expose sensitive data (keys, tokens, PII) in logs or code comments
- Use parameterized queries and built-in escaping for database/API operations
- Follow least-privilege principle: minimal permissions, scoped tokens, restricted access

**Efficient resource usage:**
- Avoid unnecessary loops, duplicate queries, or redundant operations
- Cache frequently accessed data to reduce I/O and computation
- Size data structures to actual need—no over-provisioning defaults
- Monitor baseline performance: changes should not regress against established metrics

**Modular design:**
- Functions should have a single, clear responsibility
- Avoid tight coupling; prefer composition and dependency injection
- Extract reusable logic into utilities; resist copy-paste
- Keep changes focused—don't refactor unrelated code in the same PR

**Reasoning & transparency:**
When suggesting complex solutions, AI must:
- Explain *why* a pattern was chosen over alternatives
- Surface tradeoffs and constraints (e.g., performance vs. maintainability)
- Flag non-obvious decisions (workarounds, version-specific behavior, compatibility needs)
- Link to relevant context (past incidents, performance baselines, related tickets)

**Human review checkpoints:**
- Code changes flagged as "complex" trigger explicit review gates before merge
- Design decisions with architectural impact (new services, schema changes, migrations) require approval
- Performance-sensitive paths require baseline comparison and sign-off
- Security-related code (auth, data handling, integrations) always reviewed by owner before deployment

All changes logged to Action Items before implementation, with reasoning documented for future reference.

## Theme IDs
- Production: 149898395726
- Staging: 150391423054

## Performance baseline
See `Project/Active/BMBooks_Performance_Baseline.md` — do not hardcode snapshots here.
