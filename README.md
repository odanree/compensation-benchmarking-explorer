# Compensation Benchmarking Explorer

A GraphQL API (Django + Strawberry) with a React/Next.js frontend for exploring compensation bands by role, level, location, and company size. Demonstrates schema-first GraphQL design, cursor pagination, field-level authorization, and Apollo Client integration.

## Architecture

```
┌─────────────────────────────────────────┐
│  Next.js 15 + Apollo Client             │
│  ┌──────────┐  ┌──────────┐             │
│  │ Filter   │  │ Band     │             │
│  │ Panel    │  │ Table    │             │
│  └────┬─────┘  └────┬─────┘             │
│       └──────┬───────┘                  │
│              │ GraphQL query            │
└──────────────┼──────────────────────────┘
               │ HTTP POST /graphql/
┌──────────────▼──────────────────────────┐
│  Django 5 + Strawberry GraphQL          │
│  ┌──────────────────────────────────┐   │
│  │  Query.compensation_bands        │   │
│  │  • cursor pagination             │   │
│  │  • filter input                  │   │
│  │  • p90 auth guard (field-level)  │   │
│  └────────────────┬─────────────────┘   │
└───────────────────┼─────────────────────┘
                    │ Django ORM
┌───────────────────▼─────────────────────┐
│  PostgreSQL — compensation_band table   │
└─────────────────────────────────────────┘
```

## Setup

### Backend (Docker Compose)

```bash
cd backend
cp .env.example .env
# Edit SECRET_KEY and DATABASE_PASSWORD

docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_bands
docker-compose exec web python manage.py createsuperuser  # optional
```

API: `http://localhost:8000`
GraphQL Playground: `http://localhost:8000/graphql/`

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

App: `http://localhost:3000`

## GraphQL Playground

Open `http://localhost:8000/graphql/` in your browser for an interactive GraphQL explorer.

### Sample Queries

**Browse all bands (paginated):**
```graphql
query {
  compensationBands(first: 10) {
    edges {
      node {
        role
        level
        location
        companySize
        p25
        p50
        p75
        p90
        sampleSize
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
```

**Filter by role and level:**
```graphql
query {
  compensationBands(
    first: 20
    filters: {
      role: "Senior Software Engineer"
      level: "IC5"
      companySize: "enterprise"
    }
  ) {
    edges {
      node { role level location p50 p75 }
    }
    totalCount
  }
}
```

**Next page (cursor pagination):**
```graphql
query {
  compensationBands(first: 10, after: "<endCursor from previous response>") {
    edges {
      node { role p50 }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

**Available filter options:**
```graphql
query {
  availableRoles
  availableLocations
}
```

## Field-Level Authorization (P90)

The `p90` field returns `null` for unauthenticated requests. When authenticated via Django session, the real value is returned. This is implemented at the resolver level in `apps/compensation/schema.py`:

```python
@staticmethod
def from_model(band, authenticated: bool):
    return CompensationBandType(
        ...
        p90=float(band.p90) if authenticated else None,
    )
```

## Running Tests

```bash
cd backend
pip install -r requirements/development.txt
pytest -v
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | sqlite | PostgreSQL connection URL |
| `SECRET_KEY` | insecure default | Django secret key |
| `DEBUG` | `True` | Enable debug mode |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Frontend origin |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_GRAPHQL_URL` | `http://localhost:8000/graphql/` | Backend GraphQL endpoint |
