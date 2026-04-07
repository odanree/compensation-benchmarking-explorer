# ADR 005: createBand Mutation Design — Union Return Type and Input Validation

**Date:** 2026-04-07
**Status:** Accepted

## Context

The API needed a write path for creating compensation bands. The two main design questions were:
1. How to represent the result (success vs. validation failure) in GraphQL's type system.
2. Where to enforce authentication — at the schema level, the resolver level, or both.

## Decision

### Union return type for results

The `createBand` mutation returns a **union type**:

```graphql
union CreateBandResult = CreateBandSuccess | CreateBandError

type CreateBandSuccess { band: CompensationBandType }
type CreateBandError   { messages: [String!]! }
```

Clients use inline fragments to handle both cases:

```graphql
mutation {
  createBand(input: $input) {
    ... on CreateBandSuccess { band { id p50 } }
    ... on CreateBandError   { messages }
  }
}
```

### Validation in the input type

Business rule validation is implemented as `CompensationBandInput.validate() -> list[str]`:
- `role`, `level`, `location` must be non-blank.
- `company_size` must be a valid enum value (`startup | small | mid | large | enterprise`).
- Percentiles must satisfy `0 < p25 <= p50 <= p75 <= p90`.
- `sample_size` must be >= 0.

### Authentication via `IsAuthenticated` permission class

```python
class IsAuthenticated(BasePermission):
    message = "You must be logged in to perform this action."
    def has_permission(self, source, info, **kwargs) -> bool:
        return info.context.request.user.is_authenticated

@strawberry.mutation(permission_classes=[IsAuthenticated])
def create_band(self, info, input) -> CreateBandResult: ...
```

### Duplicate detection via `get_or_create`

A band is uniquely identified by `(role, level, location, company_size)`. Submitting a duplicate returns a `CreateBandError` with a descriptive message rather than silently updating or raising a 500.

## Reasoning

**Union type over HTTP error codes:**
In GraphQL, errors can be represented two ways: as GraphQL errors (which appear in the `errors` array) or as typed union members in `data`. Using a union keeps validation failures in the type system — clients know at schema introspection time that a `CreateBandError` is possible and can handle it without special-casing the `errors` array. HTTP error codes (400, 422) are meaningless in GraphQL since all requests return HTTP 200.

**`BasePermission` over resolver-level guard:**
`permission_classes=[IsAuthenticated]` applies the check before the resolver runs and produces a standard GraphQL error with `"You must be logged in"` in the message. A manual `if not user.is_authenticated: return CreateBandError(...)` inside the resolver would mix authentication failure with application-level errors in the same return type, making client error handling ambiguous.

**Validation in the input class, not the resolver:**
`input.validate()` keeps the resolver thin and makes validation testable independently of the GraphQL execution pipeline. It also allows multiple errors to be returned at once (e.g., blank role AND invalid company_size).

**`get_or_create` over `create` + exception handling:**
`get_or_create` is atomic — it avoids a race condition between checking for duplicates and inserting. The `created` boolean tells us exactly whether we inserted or found an existing record without catching `IntegrityError`.

## Trade-offs

- **No partial updates:** `createBand` is create-only. An `updateBand` mutation would follow the same pattern with `update_or_create` semantics — not implemented here to keep scope focused.
- **Union type adds client complexity:** Clients must use inline fragments instead of a flat response shape. This is idiomatic GraphQL but requires Apollo Client union type policies (`possibleTypes`) in production setups.
- **`Annotated[Union[...], strawberry.union(...)]`** is required by Strawberry 0.235's union API. The older `strawberry.union("Name", types=(...))` call form emits a deprecation warning.

## Consequences

- `schema = strawberry.Schema(query=Query, mutation=Mutation)` — the schema now exposes both query and mutation roots.
- Unauthenticated `createBand` calls return a GraphQL-level error (not a `CreateBandError`), distinguishing auth failures from validation failures.
- Seven tests cover the mutation: success, auth rejection, duplicate, invalid percentiles, invalid company_size, blank role, and DB persistence.
