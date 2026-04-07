# ADR 002: Cursor-Based Pagination Over Offset Pagination

**Date:** 2026-04-07
**Status:** Accepted

## Context

The `compensationBands` query returns potentially hundreds of records. Pagination is required. The two standard approaches are offset pagination (`LIMIT N OFFSET M`) and cursor-based pagination (relay-style, using an opaque pointer into the result set).

## Decision

Use **cursor-based pagination** with base64-encoded primary key cursors. The query signature is:

```graphql
compensationBands(first: Int, after: String, filters: CompensationBandFilter): CompensationBandConnection
```

Cursors are encoded as `base64("CompensationBand:{pk}")`.

## Reasoning

**Stability under concurrent writes:**
Offset pagination is unstable when rows are inserted or deleted between pages. If 5 records are inserted before page 2 is fetched, `OFFSET 20` skips 5 records. Cursor pagination anchors to a specific row (`WHERE pk > cursor_pk`), so new rows don't shift existing pages.

**Performance:**
`WHERE pk > N ORDER BY pk LIMIT 20` uses the primary key index directly — O(log n) seek, O(1) scan. `OFFSET M` requires the DB to scan and discard M rows even with an index.

**Relay compatibility:**
The `CompensationBandConnection` / `CompensationBandEdge` / `PageInfo` structure follows the Relay Cursor Connections specification. Apollo Client's `InMemoryCache` can merge paginated results automatically using `keyArgs` and a custom `merge` function, enabling infinite scroll without client-side re-fetching.

**Opaque cursors (`base64`):**
Encoding as `base64("CompensationBand:{pk}")` makes cursors opaque to the client — they cannot reverse-engineer or construct cursors manually. This preserves the freedom to change the cursor implementation (e.g., switching from PK to a composite sort key) without breaking clients.

## Trade-offs

- **No random access:** Cursor pagination cannot jump to page 7 directly. For this use case (browse, filter, scroll), this is acceptable. A "jump to page" feature would require offset pagination or a hybrid approach.
- **`hasPreviousPage` is approximate:** Because we track only `after` (not `before`), `hasPreviousPage` is set to `True` whenever `after != None`. A full Relay implementation with `before`/`last` would be more precise but significantly more complex.
- **`totalCount` runs a separate COUNT query:** This adds one extra DB query per request. At this data volume it's fast, but at scale it would be cached or omitted.

## Consequences

- `encode_cursor(pk)` / `decode_cursor(cursor)` live in `schema.py` alongside the resolvers.
- Apollo Client's `merge` policy in `lib/apollo.ts` appends new `edges` to existing ones when `after` is set, enabling append-only infinite scroll.
- The `first` argument is capped at 100 server-side to prevent abuse.
