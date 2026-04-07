# ADR 003: Field-Level Authorization for P90 Compensation Data

**Date:** 2026-04-07
**Status:** Accepted

## Context

P90 compensation data (the 90th percentile total comp for a role/level/location) is commercially sensitive. In a real product, it would be gated behind a paid tier or require account verification. The API must return partial data for unauthenticated users — showing p25/p50/p75 — while hiding p90.

## Decision

Implement **field-level authorization** in the `CompensationBandType` resolver: the `p90` field returns `null` when `info.context.request.user.is_authenticated` is `False`.

```python
@staticmethod
def from_model(band: CompensationBand, authenticated: bool) -> "CompensationBandType":
    return CompensationBandType(
        ...
        p90=float(band.p90) if authenticated else None,
    )
```

The field is typed `Optional[float]` — clients must handle `null` explicitly.

## Reasoning

**Field-level over query-level authorization:**
A query-level permission check (`@strawberry.permission.BasePermission`) would reject the entire `compensationBands` query for unauthenticated users. This is too coarse — anonymous users should be able to browse the table and see most data. Field-level control allows a degraded but useful experience without authentication.

**Null over omission:**
Returning `null` (rather than omitting the field from the response) keeps the response shape consistent. Apollo Client's type policies and TypeScript types can express `p90: number | null` cleanly. Omitting the field entirely would require union types or conditional queries.

**Resolver-level over schema directive:**
Strawberry supports `@strawberry.permission` directives, but applying them at the field level requires a custom directive implementation. Handling it in `from_model(authenticated=...)` is explicit, testable, and avoids directive machinery complexity.

**No database change:**
The `p90` column is stored for all records. The authorization decision is made at read time, not write time. This means p90 data is always available for authenticated users without a separate query or table.

## Trade-offs

- **The `p90` value is in the DB regardless of auth level** — a database-level row security policy would be more defense-in-depth, but is overkill for a portfolio project.
- **`info.context` access in tests requires a wrapper object** (`_Context`) because `schema.execute_sync` doesn't wrap the context in a Django request object automatically. This is a minor test ergonomics cost.

## Consequences

- `CompensationBandType.p90` is `Optional[float]` in the schema and in TypeScript types.
- The frontend renders `"Login to view"` when `band.p90 === null`.
- Two tests cover both paths: `test_p90_hidden_for_unauthenticated` and `test_p90_visible_for_authenticated`.
