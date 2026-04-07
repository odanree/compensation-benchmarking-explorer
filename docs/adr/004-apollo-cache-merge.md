# ADR 004: Apollo Client Cache Merge Policy for Cursor Pagination

**Date:** 2026-04-07
**Status:** Accepted

## Context

The frontend fetches compensation bands with cursor pagination. When the user clicks "Next", the app fetches the next page with `after: endCursor`. Without cache configuration, Apollo Client would replace the existing cached result with the new page, losing the previous page's data.

## Decision

Configure a **custom `merge` function** in Apollo Client's `InMemoryCache` for the `compensationBands` field:

```typescript
compensationBands: {
  keyArgs: ["filters"],
  merge(existing, incoming, { args }) {
    if (!args?.after) return incoming;
    const merged = existing ? { ...existing } : { ...incoming };
    merged.edges = [...(existing?.edges ?? []), ...incoming.edges];
    merged.pageInfo = incoming.pageInfo;
    return merged;
  },
},
```

## Reasoning

**`keyArgs: ["filters"]`:**
The cache key for `compensationBands` includes only the `filters` argument, not `first` or `after`. This means all pages fetched with the same filter set share one cache entry. When filters change, the cache key changes and a fresh fetch starts from page 1.

**`merge` function appends edges:**
When `args.after` is present (i.e., this is a subsequent page), the new edges are appended to the existing ones. When `args.after` is absent (first page or filter change), `incoming` replaces `existing` entirely.

**`pageInfo` always takes the latest value:**
`pageInfo.hasNextPage` and `endCursor` must reflect the most recently fetched page, not the first page. The merge function always overwrites `pageInfo` with `incoming.pageInfo`.

**`totalCount` consistency:**
`totalCount` is not merged — it's always the count for the current filter set, which doesn't change as pages are fetched.

## Trade-offs

- **Previous-page navigation is not cache-optimized:** The "Previous" button resets `cursor` to `null` (back to page 1) rather than navigating to the true previous page. A full bidirectional cursor cache would require tracking a cursor stack. For a browse-and-filter UX, back-to-top is acceptable.
- **Cache invalidation on filter change:** When filters change, `keyArgs` produces a new cache entry, so a full refetch occurs. This is correct behavior but means frequently-changed filters always hit the network.

## Consequences

- `BandExplorer` manages `cursor` state as `string | null` (not a cursor stack).
- The "Previous" button sets `cursor = null`, returning to page 1.
- Filter changes reset `cursor = null` in `handleFiltersChange`.
- Apollo's `fetchPolicy` defaults to `cache-first`, so navigating back to a previously-seen filter set is instant.
