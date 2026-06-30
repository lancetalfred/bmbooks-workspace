# Python Review Checklist

Reference checklist for reviewing changes to `Sync/*.py` and `Tools/*.py`. Paste relevant items into a review prompt, or run the diagnostic commands directly.

Adapted from ECC's `python-reviewer` agent (github.com/affaan-m/ECC) — the checklist content was worth keeping, the "agent" wrapper wasn't.

## Diagnostic commands
```
ruff check .
mypy .
bandit -r .
```

## CRITICAL
- Mutable default arguments — `def f(x=[])` → `def f(x=None)` then `x = x or []` inside
- f-strings or `%`-formatting in SQL/API queries — use parameterized queries instead
- Bare `except: pass` — catch specific exceptions, never swallow silently
- Hardcoded secrets/tokens — must come from `os.environ`, never literal strings (see CLAUDE.md security rules)

## HIGH
- `value == None` instead of `value is None`
- Shadowing builtins (`list`, `dict`, `id`, `type` as variable names)
- Functions over ~50 lines — split by responsibility
- Functions with more than ~5 parameters — consider a dataclass instead
- Nesting depth over 4 levels — use early returns / guard clauses

## MEDIUM
- Missing type hints on public functions
- Inconsistent return types (sometimes `None`, sometimes a value, sometimes raises)
- String concatenation in loops — use `"".join(...)` or list comprehension
- Catching `Exception` broadly when a narrower exception type is known

## Project-specific (BMBooks)
- Any new Shopify API call — confirm it goes through the existing `ShopifyAPI`-style pattern in `bookscan_sync.py`, not a fresh ad-hoc `requests` call
- Any DBF read — confirm it's not reading `.dbf` files in full per CLAUDE.md rule #4 (grep only)
- Any change to tag logic — confirm it doesn't silently drop the `_cstatus-`/`_dept-` hidden tags
- Token handling — must read from `SHOPIFY_ACCESS_TOKEN` env var, never hardcoded (see 2026-06-25 token scrub)
