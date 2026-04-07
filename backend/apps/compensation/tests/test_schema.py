import pytest
from django.test import RequestFactory

from apps.compensation.schema import schema
from apps.compensation.tests.factories import CompensationBandFactory


class _Context:
    """Wraps a request so info.context.request works in execute_sync tests."""
    def __init__(self, request):
        self.request = request


def make_context(authenticated=False):
    rf = RequestFactory()
    request = rf.get("/graphql/")
    if authenticated:
        from django.contrib.auth.models import User

        # Use get_or_create so repeated calls within a test don't clash
        user, _ = User.objects.get_or_create(username="test_auth_user")
        request.user = user
    else:
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()
    return _Context(request)


@pytest.mark.django_db
class TestCompensationBandsQuery:
    def test_returns_results(self):
        CompensationBandFactory.create_batch(5, role="Software Engineer II")
        result = schema.execute_sync(
            """
            query {
                compensationBands(first: 10) {
                    edges { node { role level p50 } }
                    pageInfo { hasNextPage }
                    totalCount
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["compensationBands"]["totalCount"] == 5
        assert len(result.data["compensationBands"]["edges"]) == 5

    def test_p90_hidden_for_unauthenticated(self):
        CompensationBandFactory.create()
        result = schema.execute_sync(
            """
            query {
                compensationBands(first: 1) {
                    edges { node { p90 } }
                }
            }
            """,
            context_value=make_context(authenticated=False),
        )
        assert not result.errors
        assert result.data["compensationBands"]["edges"][0]["node"]["p90"] is None

    def test_p90_visible_for_authenticated(self):
        CompensationBandFactory.create(p90=300000)
        result = schema.execute_sync(
            """
            query {
                compensationBands(first: 1) {
                    edges { node { p90 } }
                }
            }
            """,
            context_value=make_context(authenticated=True),
        )
        assert not result.errors
        assert result.data["compensationBands"]["edges"][0]["node"]["p90"] == 300000.0

    def test_cursor_pagination(self):
        CompensationBandFactory.create_batch(10)
        result1 = schema.execute_sync(
            """
            query {
                compensationBands(first: 5) {
                    edges { cursor node { id } }
                    pageInfo { hasNextPage endCursor }
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result1.errors
        assert result1.data["compensationBands"]["pageInfo"]["hasNextPage"] is True

        cursor = result1.data["compensationBands"]["pageInfo"]["endCursor"]
        result2 = schema.execute_sync(
            f"""
            query {{
                compensationBands(first: 5, after: "{cursor}") {{
                    edges {{ node {{ id }} }}
                    pageInfo {{ hasNextPage hasPreviousPage }}
                    totalCount
                }}
            }}
            """,
            context_value=make_context(),
        )
        assert not result2.errors
        assert result2.data["compensationBands"]["pageInfo"]["hasPreviousPage"] is True
        # Total count is across all pages
        assert result2.data["compensationBands"]["totalCount"] == 10

    def test_filter_by_role(self):
        CompensationBandFactory.create(role="Software Engineer II", level="IC4")
        CompensationBandFactory.create(role="Product Manager", level="IC4")
        result = schema.execute_sync(
            """
            query {
                compensationBands(filters: { role: "Software Engineer II" }) {
                    totalCount
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["compensationBands"]["totalCount"] == 1

    def test_filter_by_company_size(self):
        CompensationBandFactory.create(company_size="startup")
        CompensationBandFactory.create(company_size="enterprise")
        result = schema.execute_sync(
            """
            query {
                compensationBands(filters: { companySize: "startup" }) {
                    totalCount
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["compensationBands"]["totalCount"] == 1

    def test_available_roles(self):
        CompensationBandFactory.create(role="Software Engineer")
        CompensationBandFactory.create(role="Product Manager")
        result = schema.execute_sync(
            """
            query { availableRoles }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert "Software Engineer" in result.data["availableRoles"]
        assert "Product Manager" in result.data["availableRoles"]

    def test_available_locations(self):
        CompensationBandFactory.create(location="San Francisco Bay Area")
        CompensationBandFactory.create(location="New York Metro", role="PM 1")
        result = schema.execute_sync(
            """
            query { availableLocations }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert "San Francisco Bay Area" in result.data["availableLocations"]

    def test_single_band_query(self):
        band = CompensationBandFactory.create(p50=200000)
        result = schema.execute_sync(
            f"""
            query {{
                compensationBand(id: "{band.pk}") {{
                    id
                    role
                    p50
                }}
            }}
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["compensationBand"]["p50"] == 200000.0

    def test_single_band_not_found(self):
        result = schema.execute_sync(
            """
            query {
                compensationBand(id: "99999") {
                    id
                }
            }
            """,
            context_value=make_context(),
        )
        assert not result.errors
        assert result.data["compensationBand"] is None
