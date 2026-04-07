# ADR 001: Use Strawberry GraphQL Over Django REST Framework

**Date:** 2026-04-07
**Status:** Accepted

## Context

The benchmarking explorer exposes compensation band data to a React frontend. The choice of API layer determines how the frontend queries data, how filtering is expressed, and how the schema evolves over time.

Compa's frontend stack uses GraphQL. The goal of this project is to demonstrate GraphQL API design — schema definition, cursor pagination, field-level authorization, and typed inputs — not REST endpoint design.

## Decision

Use **Strawberry GraphQL** (`strawberry-graphql[django]`) as the API layer. No Django REST Framework.

## Reasoning

**Strawberry over Graphene:**
- Strawberry is schema-first and Python-type-first: types are defined with `@strawberry.type` decorators on dataclasses, not metaclass magic.
- Type inference works with Python's standard `Optional`, `list`, and `dataclass` — no need for `graphene.List(graphene.NonNull(...))` wrapping.
- Active development; Graphene 3.x is largely in maintenance mode.

**GraphQL over REST for this domain:**
- The compensation band data has multiple filter dimensions (role, level, location, company_size, min_p50, max_p50). A REST API would require either a long query string convention or multiple endpoints. GraphQL's typed input objects (`CompensationBandFilter`) make filter combinations explicit and self-documenting.
- The frontend needs different field sets in different contexts (table view vs. summary card). GraphQL field selection avoids over-fetching without building custom serializer variants.
- Field-level authorization (hiding `p90` for unauthenticated users) is a natural GraphQL pattern — the resolver returns `None` based on `info.context.request.user.is_authenticated`. In REST this would require response post-processing or a separate endpoint.

**Single GraphQL endpoint:**
All queries and mutations go through `POST /graphql/`. Django's URL config has one route, reducing routing complexity.

## Trade-offs

- **No browsable API:** DRF's browsable API is a useful debugging tool that Strawberry doesn't replicate. Strawberry's built-in GraphiQL playground (`/graphql/` in DEBUG mode) fills this role for GraphQL-shaped exploration.
- **N+1 risk:** Without DataLoader, nested resolvers can cause N+1 queries. At the current schema depth (flat `CompensationBand` with no nested relations), this is not a concern. A future schema with `CompensationBand.submissions` would require DataLoader.
- **Strawberry's Django integration** requires `strawberry.django` in `INSTALLED_APPS` and uses `GraphQLView` from `strawberry.django.views`. This is well-supported but less mature than DRF's ecosystem.

## Consequences

- The schema is defined entirely in `apps/compensation/schema.py`.
- Tests use `schema.execute_sync(query, context_value=...)` — no HTTP client needed for schema-level tests.
- The `info.context` object must be wrapped in a container class in tests (`_Context`) because `execute_sync` passes the context value directly, not as a Django request wrapper.
