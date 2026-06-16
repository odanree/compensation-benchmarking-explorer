# ADR 004: Apollo Client Cache Keying for Cursor Pagination

**Date:** 2026-04-07
**Status:** Accepted (revised 2026-06-16: replaced append-style merge with per-cursor cache entries — see "Revision" below)

## Context

The frontend fetches solar cost bands with cursor pagination. The UI uses explicit **Next** and **Previous** buttons (not infinite scroll). Each click should show exactly one page of `PAGE_SIZE` rows.

Apollo's default cache strategy treats every distinct variable combination as a separate cache entry. With cursor pagination, that's the desired behavior for explicit-pagination UIs: each `(filters, after)` pair caches its own page.

## Decision

Configure `keyArgs` on the `costBands` field to include both `filters` and `after`:

```typescript
costBands: {
  keyArgs: ["filters", "after"],
},
```

No custom `merge` function — Apollo's default merge (replace) gives correct pagination behavior: each Next click loads a new page and shows only that page; each Previous click loads the prior page (currently capped at page 1 — see Trade-offs).

## Reasoning

**`keyArgs: ["filters", "after"]`:**
Each `(filters, after)` combination is a distinct cache entry. Re-visiting a page that's already been fetched serves from cache instantly without a network round-trip. Changing filters or cursor invalidates the entry and fetches fresh.

**No `merge` function needed:**
Apollo's default behavior for a field returning a new value is to replace the cached value with the incoming one. For per-cursor cache entries, this is exactly what we want — each page is its own entry, no inter-page merging required.

**`totalCount` per-cursor:**
`totalCount` ships with every page response. Since each page is its own cache entry, the count stays consistent with what the user sees.

## Trade-offs

- **Cursor stack is client-side only:** Previous-page navigation uses an in-memory `cursorStack` in `BandExplorer`. A page refresh resets the stack to `[null]`, so reloading on page 3 lands the user on page 1. Persisting the stack to the URL would fix this; not done because the table is meant for browse-and-filter, not deep-linked navigation.
- **Memory footprint scales with pages visited:** Each distinct `(filters, after)` pair occupies its own cache slot until garbage-collected. For a 68-row dataset with 20-row pages, this means at most 4 cache entries per filter combo. Bounded.
- **`hasPreviousPage` overridden client-side:** The server's `pageInfo.hasPreviousPage` is approximate (set to `true` whenever `after != null` — see ADR 002). The client overrides it with `cursorStack.length > 1`, which is correct.

## Consequences

- `BandExplorer` manages a `cursorStack: (string | null)[]` initialized to `[null]`.
- Current page's cursor is `cursorStack[cursorStack.length - 1]`.
- The "Previous" button pops the top of the stack, revealing the prior page's cursor.
- The "Next" button pushes the current page's `endCursor` onto the stack.
- Filter changes reset the stack to `[null]` in `handleFiltersChange`.
- Apollo's `fetchPolicy` defaults to `cache-first`, so re-visiting a previously-fetched page is instant.

## Revision (2026-06-16)

**Original design** used a custom `merge` function that appended new edges to the existing array — infinite-scroll semantics. This was a mismatch with the UI: the page has explicit Next/Previous buttons, which users expect to **replace** the visible rows rather than append below. From a viewer's scroll position at the top of the page, clicking Next made no visible change (new rows appended below the fold), so it looked broken.

The fix was to drop the merge function and let Apollo's default replace behavior handle each cursor as its own page. If we ever switch the UI to infinite scroll, the append-style merge from the original ADR is the right pattern to bring back.
